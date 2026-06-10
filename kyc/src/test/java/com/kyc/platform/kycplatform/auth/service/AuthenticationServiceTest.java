package com.kyc.platform.kycplatform.auth.service;

import com.kyc.platform.kycplatform.auth.domain.Role;
import com.kyc.platform.kycplatform.auth.domain.User;
import com.kyc.platform.kycplatform.auth.dto.AuthResponse;
import com.kyc.platform.kycplatform.auth.dto.LoginRequest;
import com.kyc.platform.kycplatform.auth.dto.RefreshTokenRequest;
import com.kyc.platform.kycplatform.auth.repository.RefreshTokenRepository;
import com.kyc.platform.kycplatform.auth.repository.RoleRepository;
import com.kyc.platform.kycplatform.auth.repository.UserRepository;
import com.kyc.platform.kycplatform.auth.shared.exception.AuthenticationException;
import com.kyc.platform.kycplatform.auth.shared.exception.TokenRevokedException;
import com.kyc.platform.kycplatform.config.JwtProperties;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Spy;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.time.Instant;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AuthenticationServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private RoleRepository roleRepository;

    @Mock
    private RefreshTokenRepository refreshTokenRepository;

    @Mock
    private JwtService jwtService;

    @Mock
    private PasswordEncoder passwordEncoder;

    @Mock
    private AuthenticationManager authenticationManager;

    @Mock
    private JwtProperties jwtProperties;

    @InjectMocks
    @Spy
    private AuthenticationServiceImpl authenticationService;

    private User testUser;
    private Role testRole;

    @BeforeEach
    void setUp() {
        testRole = Role.builder()
                .id(UUID.randomUUID())
                .name(Role.RoleName.COMPLIANCE_ANALYST)
                .description("Test role")
                .build();

        testUser = User.builder()
                .id(UUID.randomUUID())
                .username("testuser")
                .email("test@example.com")
                .passwordHash("$2a$12$encodedPassword")
                .firstName("Test")
                .lastName("User")
                .enabled(true)
                .locked(false)
                .roles(Set.of(testRole))
                .createdAt(Instant.now())
                .build();
    }

    @Test
    void shouldLoginUserSuccessfully() {
        LoginRequest request = new LoginRequest();
        request.setUsername("testuser");
        request.setPassword("password");

        Authentication auth = new UsernamePasswordAuthenticationToken("testuser", "password");
        
        when(authenticationManager.authenticate(any())).thenReturn(auth);
        when(userRepository.findByUsername("testuser")).thenReturn(Optional.of(testUser));
        when(jwtService.generateAccessToken(any())).thenReturn("access-token");
        when(jwtService.generateRefreshToken()).thenReturn("refresh-token");
        when(jwtService.hashToken(any())).thenReturn("hashed-token");
        when(jwtProperties.expirationTime()).thenReturn(3600000L);

        AuthResponse response = authenticationService.login(request);

        assertNotNull(response);
        assertEquals("access-token", response.getAccessToken());
        assertEquals("refresh-token", response.getRefreshToken());
        verify(userRepository).save(any(User.class));
    }

    @Test
    void shouldFailLoginWithLockedAccount() {
        testUser.setLocked(true);
        
        LoginRequest request = new LoginRequest();
        request.setUsername("testuser");
        request.setPassword("password");

        Authentication auth = new UsernamePasswordAuthenticationToken("testuser", "password");
        
        when(authenticationManager.authenticate(any())).thenReturn(auth);
        when(userRepository.findByUsername("testuser")).thenReturn(Optional.of(testUser));

        assertThrows(AuthenticationException.class, () -> authenticationService.login(request));
    }

    @Test
    void shouldFailRefreshWithInvalidToken() {
        RefreshTokenRequest request = new RefreshTokenRequest();
        request.setRefreshToken("invalid-token");

        when(jwtService.hashToken("invalid-token")).thenReturn("hashed-invalid");
        when(refreshTokenRepository.findByTokenHashAndRevokedFalse("hashed-invalid"))
                .thenReturn(Optional.empty());

        assertThrows(TokenRevokedException.class, () -> authenticationService.refresh(request));
    }

    @Test
    void shouldLogoutSuccessfully() {
        authenticationService.logout("valid-token");
        
        verify(refreshTokenRepository).findByTokenHashAndRevokedFalse(any());
    }
}
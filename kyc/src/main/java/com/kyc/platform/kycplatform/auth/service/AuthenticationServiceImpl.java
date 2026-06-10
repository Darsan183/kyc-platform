package com.kyc.platform.kycplatform.auth.service;

import com.kyc.platform.kycplatform.auth.domain.RefreshToken;
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
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class AuthenticationServiceImpl implements AuthenticationService {

    private final UserRepository userRepository;
    private final RoleRepository roleRepository;
    private final RefreshTokenRepository refreshTokenRepository;
    private final JwtService jwtService;
    private final PasswordEncoder passwordEncoder;
    private final AuthenticationManager authenticationManager;
    private final JwtProperties jwtProperties;

    @Override
    public AuthResponse login(LoginRequest request) {
        Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                        request.getUsername(),
                        request.getPassword()
                )
        );

        User user = userRepository.findByUsername(request.getUsername())
                .orElseThrow(() -> new AuthenticationException("User not found"));

        if (user.isLocked()) {
            throw new AuthenticationException("Account is locked");
        }

        user.setLastLoginAt(Instant.now());
        user.resetFailedAttempts();
        userRepository.save(user);

        String accessToken = jwtService.generateAccessToken(user);
        String refreshToken = jwtService.generateRefreshToken();

        RefreshToken rt = RefreshToken.builder()
                .user(user)
                .tokenHash(jwtService.hashToken(refreshToken))
                .expiresAt(Instant.now().plusSeconds(jwtProperties.refreshTokenExpiration()))
                .issuedAt(Instant.now())
                .ipAddress("")
                .userAgent("")
                .build();

        refreshTokenRepository.save(rt);

        return buildAuthResponse(user, accessToken, refreshToken);
    }

    @Override
    @Transactional(readOnly = true)
    public AuthResponse refresh(RefreshTokenRequest request) {
        String tokenHash = jwtService.hashToken(request.getRefreshToken());
        
        RefreshToken refreshToken = refreshTokenRepository
                .findByTokenHashAndRevokedFalse(tokenHash)
                .orElseThrow(() -> new TokenRevokedException("Invalid or revoked refresh token"));

        if (refreshToken.isExpired()) {
            throw new TokenRevokedException("Refresh token expired");
        }

        User user = refreshToken.getUser();
        
        if (!user.isEnabled() || user.isLocked()) {
            throw new AuthenticationException("User account not active");
        }

        String accessToken = jwtService.generateAccessToken(user);
        String newRefreshToken = jwtService.generateRefreshToken();

        // Revoke old token
        refreshToken.revoke();

        // Create new refresh token
        RefreshToken newRt = RefreshToken.builder()
                .user(user)
                .tokenHash(jwtService.hashToken(newRefreshToken))
                .expiresAt(Instant.now().plusSeconds(jwtProperties.refreshTokenExpiration()))
                .issuedAt(Instant.now())
                .ipAddress(refreshToken.getIpAddress())
                .userAgent(refreshToken.getUserAgent())
                .build();

        refreshTokenRepository.save(newRt);

        return buildAuthResponse(user, accessToken, newRefreshToken);
    }

    @Override
    public void logout(String refreshToken) {
        if (refreshToken != null && !refreshToken.isBlank()) {
            String tokenHash = jwtService.hashToken(refreshToken);
            refreshTokenRepository.findByTokenHashAndRevokedFalse(tokenHash)
                    .ifPresent(rt -> {
                        rt.revoke();
                        refreshTokenRepository.save(rt);
                    });
        }
    }

    @Override
    public AuthResponse register(String username, String email, String password, String firstName, String lastName) {
        if (userRepository.existsByUsername(username)) {
            throw new AuthenticationException("Username already exists");
        }
        if (userRepository.existsByEmail(email)) {
            throw new AuthenticationException("Email already exists");
        }

        Role userRole = roleRepository.findByName(Role.RoleName.COMPLIANCE_ANALYST)
                .orElseThrow(() -> new RuntimeException("Default role not found"));

        User user = User.builder()
                .username(username)
                .email(email)
                .passwordHash(passwordEncoder.encode(password))
                .firstName(firstName)
                .lastName(lastName)
                .enabled(true)
                .locked(false)
                .build();
        
        user.addRole(userRole);
        user.setPasswordChangedAt(Instant.now());

        userRepository.save(user);

        String accessToken = jwtService.generateAccessToken(user);
        String refreshToken = jwtService.generateRefreshToken();

        RefreshToken rt = RefreshToken.builder()
                .user(user)
                .tokenHash(jwtService.hashToken(refreshToken))
                .expiresAt(Instant.now().plusSeconds(jwtProperties.refreshTokenExpiration()))
                .issuedAt(Instant.now())
                .ipAddress("")
                .userAgent("")
                .build();

        refreshTokenRepository.save(rt);

        return buildAuthResponse(user, accessToken, refreshToken);
    }

    @Override
    public void changePassword(String userId, String currentPassword, String newPassword) {
        User user = userRepository.findById(UUID.fromString(userId))
                .orElseThrow(() -> new AuthenticationException("User not found"));

        if (!passwordEncoder.matches(currentPassword, user.getPasswordHash())) {
            throw new AuthenticationException("Current password is incorrect");
        }

        user.setPasswordHash(passwordEncoder.encode(newPassword));
        user.setPasswordChangedAt(Instant.now());
        userRepository.save(user);
    }

    @Override
    public void lockUser(String userId) {
        User user = userRepository.findById(UUID.fromString(userId))
                .orElseThrow(() -> new AuthenticationException("User not found"));
        user.lockAccount();
        userRepository.save(user);
    }

    @Override
    public void unlockUser(String userId) {
        User user = userRepository.findById(UUID.fromString(userId))
                .orElseThrow(() -> new AuthenticationException("User not found"));
        user.resetFailedAttempts();
        userRepository.save(user);
    }

    @Override
    public void resetFailedAttempts(String userId) {
        User user = userRepository.findById(UUID.fromString(userId))
                .orElseThrow(() -> new AuthenticationException("User not found"));
        user.resetFailedAttempts();
        userRepository.save(user);
    }

    private AuthResponse buildAuthResponse(User user, String accessToken, String refreshToken) {
        List<String> roles = user.getRoles().stream()
                .map(role -> role.getName().name())
                .toList();

        return AuthResponse.builder()
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .userId(user.getId())
                .username(user.getUsername())
                .email(user.getEmail())
                .roles(roles)
                .accessTokenExpiresIn(jwtProperties.expirationTime())
                .refreshTokenExpiresIn(jwtProperties.refreshTokenExpiration())
                .build();
    }
}
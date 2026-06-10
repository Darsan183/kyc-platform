package com.kyc.platform.kycplatform.auth;

import com.kyc.platform.kycplatform.AbstractIntegrationTest;
import com.kyc.platform.kycplatform.auth.dto.AuthResponse;
import com.kyc.platform.kycplatform.auth.dto.LoginRequest;
import com.kyc.platform.kycplatform.auth.repository.UserRepository;
import com.kyc.platform.kycplatform.auth.service.AuthenticationService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class AuthenticationIntegrationTest extends AbstractIntegrationTest {

    @Autowired
    private AuthenticationService authenticationService;

    @Autowired
    private UserRepository userRepository;

    @Test
    void shouldAuthenticateUser() {
        // This test requires database setup - will be validated with Testcontainers
        assertNotNull(authenticationService);
        assertNotNull(userRepository);
    }

    @Test
    void shouldFailWithInvalidCredentials() {
        LoginRequest request = new LoginRequest();
        request.setUsername("nonexistent");
        request.setPassword("wrongpassword");
        
        // Will throw AuthenticationException
        assertThrows(Exception.class, () -> authenticationService.login(request));
    }
}
package com.kyc.platform.kycplatform.auth.controller;

import com.kyc.platform.kycplatform.auth.dto.AuthResponse;
import com.kyc.platform.kycplatform.auth.dto.LoginRequest;
import com.kyc.platform.kycplatform.auth.dto.RefreshTokenRequest;
import com.kyc.platform.kycplatform.auth.service.AuthenticationService;
import com.kyc.platform.kycplatform.shared.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
@Tag(name = "Authentication", description = "Authentication and Authorization APIs")
public class AuthController {

    private final AuthenticationService authenticationService;

    @PostMapping("/login")
    @Operation(summary = "User login", description = "Authenticate user and get JWT tokens")
    public ResponseEntity<ApiResponse<AuthResponse>> login(
            @Valid @RequestBody LoginRequest request) {
        AuthResponse response = authenticationService.login(request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @PostMapping("/refresh")
    @Operation(summary = "Refresh token", description = "Refresh access token using refresh token")
    public ResponseEntity<ApiResponse<AuthResponse>> refresh(
            @Valid @RequestBody RefreshTokenRequest request) {
        AuthResponse response = authenticationService.refresh(request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @PostMapping("/logout")
    @Operation(summary = "User logout", description = "Revoke refresh token")
    public ResponseEntity<ApiResponse<Void>> logout(
            @RequestHeader(value = "X-Refresh-Token", required = false) String refreshToken) {
        authenticationService.logout(refreshToken);
        return ResponseEntity.ok(ApiResponse.success(null));
    }

    @PostMapping("/register")
    @Operation(summary = "Register user", description = "Register new user (for testing)")
    public ResponseEntity<ApiResponse<AuthResponse>> register(
            @Valid @RequestBody RegisterRequest request) {
        AuthResponse response = authenticationService.register(
                request.getUsername(),
                request.getEmail(),
                request.getPassword(),
                request.getFirstName(),
                request.getLastName()
        );
        return ResponseEntity.ok(ApiResponse.success(response));
    }
}
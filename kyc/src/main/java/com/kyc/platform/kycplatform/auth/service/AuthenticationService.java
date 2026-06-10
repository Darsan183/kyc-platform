package com.kyc.platform.kycplatform.auth.service;

import com.kyc.platform.kycplatform.auth.domain.User;
import com.kyc.platform.kycplatform.auth.dto.AuthResponse;
import com.kyc.platform.kycplatform.auth.dto.LoginRequest;
import com.kyc.platform.kycplatform.auth.dto.RefreshTokenRequest;
import com.kyc.platform.kycplatform.auth.shared.exception.AuthenticationException;

public interface AuthenticationService {

    AuthResponse login(LoginRequest request);

    AuthResponse refresh(RefreshTokenRequest request);

    void logout(String refreshToken);

    AuthResponse register(String username, String email, String password, String firstName, String lastName);

    void changePassword(String userId, String currentPassword, String newPassword);

    void lockUser(String userId);

    void unlockUser(String userId);

    void resetFailedAttempts(String userId);
}
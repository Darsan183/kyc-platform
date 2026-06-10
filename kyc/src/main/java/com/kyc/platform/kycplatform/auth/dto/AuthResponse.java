package com.kyc.platform.kycplatform.auth.dto;

import lombok.*;

import java.util.List;
import java.util.UUID;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AuthResponse {

    private String accessToken;
    private String refreshToken;
    private UUID userId;
    private String username;
    private String email;
    private List<String> roles;
    private long accessTokenExpiresIn;
    private long refreshTokenExpiresIn;
}
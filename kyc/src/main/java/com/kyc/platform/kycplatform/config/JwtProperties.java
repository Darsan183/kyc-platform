package com.kyc.platform.kycplatform.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.ConstructorBinding;

@ConstructorBinding
@ConfigurationProperties(prefix = "app.security.jwt")
public record JwtProperties(
        String secret,
        String issuer,
        long expirationTime,
        long refreshTokenExpiration
) {
    public JwtProperties() {
        this("", "kyc-platform", 3600000L, 86400000L);
    }

    public String header() {
        return "Authorization";
    }

    public String tokenPrefix() {
        return "Bearer";
    }
}
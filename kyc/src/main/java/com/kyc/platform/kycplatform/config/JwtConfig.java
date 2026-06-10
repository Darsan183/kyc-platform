package com.kyc.platform.kycplatform.config;

import io.json.jwt.Jwts;
import io.json.jwt.security.JwsSignatureAlgorithm;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import javax.crypto.SecretKey;
import java.util.Base64;

@Slf4j
@Configuration
@EnableConfigurationProperties(JwtProperties.class)
public class JwtConfig {

    private final JwtProperties jwtProperties;

    public JwtConfig(JwtProperties jwtProperties) {
        this.jwtProperties = jwtProperties;
    }

    @PostConstruct
    public void validate() {
        if (jwtProperties.secret() == null || jwtProperties.secret().isBlank()) {
            log.warn("JWT secret not configured - using default for development");
        }
    }

    @Bean
    public SecretKey jwtSecretKey() {
        String secret = jwtProperties.secret();
        if (secret == null || secret.isBlank()) {
            secret = Base64.getEncoder().encodeToString(
                    "default-secret-key-for-development-minimum-256-bits-please-change".getBytes()
            );
        }
        return Jwts.SIG.HS256.key().build(secret.getBytes());
    }
}
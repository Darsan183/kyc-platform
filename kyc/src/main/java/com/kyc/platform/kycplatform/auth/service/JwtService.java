package com.kyc.platform.kycplatform.auth.service;

import com.kyc.platform.kycplatform.auth.domain.User;
import com.nimbusds.jose.JOSEException;
import com.nimbusds.jose.JWSAlgorithm;
import com.nimbusds.jose.JWSHeader;
import com.nimbusds.jose.JWSSigner;
import com.nimbusds.jose.JWSVerifier;
import com.nimbusds.jose.crypto.MACSigner;
import com.nimbusds.jose.crypto.MACVerifier;
import com.nimbusds.jose.JWSObject;
import com.nimbusds.jose.JWTClaimsSet;
import com.nimbusds.jose.JWTParser;
import com.nimbusds.jose.ParseException;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
@Slf4j
public class JwtService {

    private final com.kyc.platform.kycplatform.config.JwtProperties jwtProperties;
    private JWSSigner signer;
    private JWSVerifier verifier;

    public JwtService(com.kyc.platform.kycplatform.config.JwtProperties jwtProperties) {
        this.jwtProperties = jwtProperties;
    }

    @PostConstruct
    public void init() {
        String secret = jwtProperties.secret();
        if (secret == null || secret.isBlank() || secret.contains("default") || secret.length() < 32) {
            throw new IllegalStateException(
                "JWT secret must be configured with at least 32 characters for production security. " +
                "Set app.security.jwt.secret environment variable.");
        }
        byte[] secretBytes = secret.getBytes();
        this.signer = new MACSigner(secretBytes);
        this.verifier = new MACVerifier(secretBytes);
    }

    public String generateAccessToken(User user) {
        try {
            Map<String, Object> claims = new HashMap<>();
            claims.put("userId", user.getId().toString());
            claims.put("email", user.getEmail());
            claims.put("roles", user.getRoles().stream()
                    .map(role -> role.getName().name())
                    .toList());

            JWTClaimsSet.Builder builder = new JWTClaimsSet.Builder()
                    .subject(user.getUsername())
                    .issuer(jwtProperties.issuer())
                    .expirationTime(new Date(System.currentTimeMillis() + jwtProperties.expirationTime()))
                    .claim("userId", user.getId().toString())
                    .claim("email", user.getEmail())
                    .claim("roles", user.getRoles().stream()
                            .map(role -> role.getName().name())
                            .toList());

            JWSObject jwsObject = new JWSObject(new JWSHeader(JWSAlgorithm.HS256), builder.build());
            jwsObject.sign(signer);
            return jwsObject.serialize();
        } catch (JOSEException e) {
            throw new RuntimeException("Failed to generate token", e);
        }
    }

    public String generateRefreshToken() {
        return UUID.randomUUID().toString() + "-" + System.currentTimeMillis();
    }

    public String hashToken(String token) {
        try {
            java.security.MessageDigest md = java.security.MessageDigest.getInstance("SHA-256");
            byte[] digest = md.digest(token.getBytes());
            return java.util.Base64.getEncoder().encodeToString(digest);
        } catch (Exception e) {
            throw new RuntimeException("Failed to hash token", e);
        }
    }

    public String extractUsername(String token) {
        try {
            JWSObject jwsObject = JWTParser.parse(token);
            return jwsObject.getPayload().toJSONObject().getAsString("sub");
        } catch (ParseException e) {
            log.warn("Failed to extract username from token", e);
            return null;
        }
    }

    public boolean validateToken(String token) {
        try {
            JWSObject jwsObject = JWTParser.parse(token);
            return jwsObject.verify(verifier) && 
                   jwsObject.getPayload().toJSONObject().getAsString("iss").equals(jwtProperties.issuer());
        } catch (ParseException | JOSEException e) {
            log.warn("Token validation failed", e);
            return false;
        }
    }

    public Date getExpirationDate(String token) {
        try {
            JWSObject jwsObject = JWTParser.parse(token);
            return jwsObject.getPayload().getExpirationTime();
        } catch (ParseException e) {
            log.warn("Failed to get expiration date", e);
            return null;
        }
    }
}
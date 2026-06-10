package com.kyc.platform.kycplatform.config;

import com.nimbusds.jose.JWSObject;
import com.nimbusds.jose.JWTParser;
import com.nimbusds.jose.JOSEException;
import com.nimbusds.jose.crypto.MACVerifier;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpHeaders;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtProperties jwtProperties;

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain) throws ServletException, IOException {

        String token = resolveToken(request);

        if (token != null && validateToken(token)) {
            authenticateToken(token, request);
        }

        filterChain.doFilter(request, response);
    }

    private String resolveToken(HttpServletRequest request) {
        String bearerToken = request.getHeader(HttpHeaders.AUTHORIZATION);
        if (StringUtils.hasText(bearerToken) &&
            bearerToken.startsWith(jwtProperties.tokenPrefix())) {
            return bearerToken.substring(jwtProperties.tokenPrefix().length() + 1);
        }
        return null;
    }

    private boolean validateToken(String token) {
        try {
            JWSObject jwsObject = JWTParser.parse(token);
            byte[] secretBytes = jwtProperties.secret().getBytes();
            MACVerifier verifier = new MACVerifier(secretBytes);

            // Verify signature
            if (!jwsObject.verify(verifier)) {
                log.warn("Invalid JWT signature");
                return false;
            }

            // Verify issuer
            var payload = jwsObject.getPayload().toJSONObject();
            if (!payload.getAsString("iss").equals(jwtProperties.issuer())) {
                log.warn("Invalid JWT issuer: {}", payload.getAsString("iss"));
                return false;
            }

            // Verify expiration
            Date expiration = jwsObject.getPayload().getExpirationTime();
            if (expiration != null && expiration.before(new Date())) {
                log.warn("JWT token expired at: {}", expiration);
                return false;
            }

            return true;
        } catch (Exception e) {
            log.warn("Token validation failed", e);
            return false;
        }
    }

    private void authenticateToken(String token, HttpServletRequest request) {
        try {
            JWSObject jwsObject = JWTParser.parse(token);
            String username = jwsObject.getPayload().toJSONObject().getAsString("sub");

            var rolesObj = jwsObject.getPayload().toJSONObject().getAsString("roles");
            List<String> roles;
            if (rolesObj instanceof String str && str.startsWith("[")) {
                roles = com.fasterxml.jackson.databind.ObjectMapper.newInstance()
                    .readValue(str, java.util.List.class);
            } else if (rolesObj instanceof java.util.List<?> lst) {
                roles = lst.stream()
                    .map(Object::toString)
                    .collect(Collectors.toList());
            } else {
                roles = java.util.Collections.emptyList();
            }

            var authorities = roles.stream()
                .map(role -> new SimpleGrantedAuthority("ROLE_" + role))
                .collect(Collectors.toList());

            var authentication = new UsernamePasswordAuthenticationToken(
                username, null, authorities);

            SecurityContextHolder.getContext().setAuthentication(authentication);
        } catch (Exception e) {
            log.warn("Failed to authenticate token", e);
        }
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        String path = request.getServletPath();
        return path.startsWith("/api/v1/auth/") ||
               path.startsWith("/v3/api-docs/") ||
               path.startsWith("/swagger-ui/") ||
               path.startsWith("/actuator/");
    }
}
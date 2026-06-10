package com.kyc.platform.kycplatform.shared.ratelimit;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.util.Map;
import java.util.concurrent.*;

@Slf4j
@Component
public class RateLimitFilter extends org.springframework.web.filter.OncePerRequestFilter {

    private final Map<String, TokenBucket> buckets = new ConcurrentHashMap<>();
    private final int capacity = 100;
    private final Duration refillPeriod = Duration.ofMinutes(1);
    private final ScheduledExecutorService cleanupScheduler = Executors.newSingleThreadScheduledExecutor();

    public RateLimitFilter() {
        cleanupScheduler.scheduleAtFixedRate(this::cleanupExpiredBuckets, 5, 5, TimeUnit.MINUTES);
    }

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain) throws ServletException, IOException {

        String ip = request.getRemoteAddr();
        TokenBucket bucket = buckets.computeIfAbsent(ip, k -> new TokenBucket(capacity, refillPeriod));

        if (bucket.tryConsume()) {
            filterChain.doFilter(request, response);
        } else {
            log.warn("Rate limit exceeded for IP: {}", ip);
            response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
            response.setContentType("application/json");
            response.getWriter().write("{\"error\":\"Rate limit exceeded\",\"retryAfter\":" + bucket.getSecondsUntilRefill() + "}");
        }
    }

    private void cleanupExpiredBuckets() {
        Instant now = Instant.now();
        buckets.entrySet().removeIf(entry -> 
            Duration.between(entry.getValue().getLastAccess(), now).compareTo(Duration.ofHours(1)) > 0
        );
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        String path = request.getServletPath();
        return path.startsWith("/health") || path.startsWith("/actuator/health") || path.startsWith("/api/v1/auth");
    }

    private static class TokenBucket {
        private final int capacity;
        private final Duration refillPeriod;
        private volatile int tokens;
        private volatile long lastRefillTimestamp;
        private volatile Instant lastAccess = Instant.now();

        TokenBucket(int capacity, Duration refillPeriod) {
            this.capacity = capacity;
            this.refillPeriod = refillPeriod;
            this.tokens = capacity;
            this.lastRefillTimestamp = System.currentTimeMillis();
        }

        boolean tryConsume() {
            refill();
            lastAccess = Instant.now();
            if (tokens > 0) {
                tokens--;
                return true;
            }
            return false;
        }

        private synchronized void refill() {
            long now = System.currentTimeMillis();
            if (now - lastRefillTimestamp >= refillPeriod.toMillis()) {
                tokens = capacity;
                lastRefillTimestamp = now;
            }
        }

        long getSecondsUntilRefill() {
            return Math.max(0, (refillPeriod.toMillis() - (System.currentTimeMillis() - lastRefillTimestamp)) / 1000);
        }

        Instant getLastAccess() {
            return lastAccess;
        }
    }
}
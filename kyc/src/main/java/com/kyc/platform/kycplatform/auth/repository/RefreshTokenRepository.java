package com.kyc.platform.kycplatform.auth.repository;

import com.kyc.platform.kycplatform.auth.domain.RefreshToken;
import com.kyc.platform.kycplatform.auth.domain.User;
import com.kyc.platform.kycplatform.infrastructure.BaseRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface RefreshTokenRepository extends BaseRepository<RefreshToken> {

    Optional<RefreshToken> findByTokenHashAndRevokedFalse(String tokenHash);

    List<RefreshToken> findByUserAndRevokedFalse(User user);

    @Modifying
    @Query("UPDATE RefreshToken rt SET rt.revoked = true, rt.revokedAt = CURRENT_TIMESTAMP WHERE rt.user = ?1 AND rt.revoked = false")
    void revokeAllUserTokens(User user);

    @Modifying
    @Query("DELETE FROM RefreshToken rt WHERE rt.expiresAt < CURRENT_TIMESTAMP")
    void deleteExpiredTokens();

    List<RefreshToken> findByUserIdAndRevokedFalse(UUID userId);
}
package com.kyc.platform.kycplatform.auth.repository;

import com.kyc.platform.kycplatform.auth.domain.User;
import com.kyc.platform.kycplatform.infrastructure.BaseRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends BaseRepository<User> {

    Optional<User> findByUsername(String username);

    Optional<User> findByEmail(String email);

    boolean existsByUsername(String username);

    boolean existsByEmail(String email);
}
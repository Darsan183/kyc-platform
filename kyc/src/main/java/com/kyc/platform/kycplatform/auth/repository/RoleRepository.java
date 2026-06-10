package com.kyc.platform.kycplatform.auth.repository;

import com.kyc.platform.kycplatform.auth.domain.RefreshToken;
import com.kyc.platform.kycplatform.auth.domain.Role;
import com.kyc.platform.kycplatform.infrastructure.BaseRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface RoleRepository extends BaseRepository<Role> {

    Optional<Role> findByName(Role.RoleName name);

    boolean existsByName(Role.RoleName name);
}
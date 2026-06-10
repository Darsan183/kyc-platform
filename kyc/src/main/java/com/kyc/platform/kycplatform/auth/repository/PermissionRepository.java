package com.kyc.platform.kycplatform.auth.repository;

import com.kyc.platform.kycplatform.auth.domain.Permission;
import com.kyc.platform.kycplatform.infrastructure.BaseRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface PermissionRepository extends BaseRepository<Permission> {

    Optional<Permission> findByName(String name);

    List<Permission> findByNameIn(List<String> names);

    boolean existsByName(String name);
}
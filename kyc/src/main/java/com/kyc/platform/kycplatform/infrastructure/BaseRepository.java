package com.kyc.platform.kycplatform.infrastructure;

import com.kyc.platform.kycplatform.domain.BaseEntity;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.repository.NoRepositoryBean;

import java.util.Optional;
import java.util.UUID;

@NoRepositoryBean
public interface BaseRepository<T extends BaseEntity> extends JpaRepository<T, UUID> {
    
    default Optional<T> findActiveById(UUID id) {
        return findById(id);
    }

    default Page<T> findAllActive(Pageable pageable) {
        return findAll(pageable);
    }
}
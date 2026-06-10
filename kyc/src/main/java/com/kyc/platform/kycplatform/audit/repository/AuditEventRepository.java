package com.kyc.platform.kycplatform.audit.repository;

import com.kyc.platform.kycplatform.audit.domain.AuditEvent;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface AuditEventRepository extends JpaRepository<AuditEvent, UUID> {
    Page<AuditEvent> findByEntityType(String entityType, Pageable pageable);
    Page<AuditEvent> findByUserId(String userId, Pageable pageable);
}
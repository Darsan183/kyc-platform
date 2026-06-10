package com.kyc.platform.kycplatform.audit.service;

import com.kyc.platform.kycplatform.audit.domain.AuditEvent;
import com.kyc.platform.kycplatform.audit.repository.AuditEventRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class AuditService {

    private final AuditEventRepository auditEventRepository;

    public void logEvent(String action, String entityType, UUID entityId, 
                        String userId, String ipAddress, String userAgent, 
                        String oldValue, String newValue) {
        AuditEvent event = AuditEvent.builder()
                .action(action)
                .entityType(entityType)
                .entityId(entityId)
                .userId(userId)
                .ipAddress(ipAddress)
                .userAgent(userAgent)
                .oldValue(oldValue)
                .newValue(newValue)
                .createdAt(Instant.now())
                .build();
        
        auditEventRepository.save(event);
        log.debug("Audit event logged: {} on {}", action, entityType);
    }

    public void logAuthentication(String username, String action, String ipAddress, boolean success) {
        AuditEvent event = AuditEvent.builder()
                .action("AUTH_" + action)
                .entityType("USER")
                .userId(username)
                .ipAddress(ipAddress)
                .newValue("success=" + success)
                .createdAt(Instant.now())
                .build();
        
        auditEventRepository.save(event);
    }
}
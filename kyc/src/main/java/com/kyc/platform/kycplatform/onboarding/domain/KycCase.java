package com.kyc.platform.kycplatform.onboarding.domain;

import com.kyc.platform.kycplatform.domain.BaseEntityWithVersion;
import com.kyc.platform.kycplatform.onboarding.domain.enums.CaseStatus;
import jakarta.persistence.*;
import lombok.*;

import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "kyc_cases")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class KycCase extends BaseEntityWithVersion {

    @Column(name = "case_reference", nullable = false, unique = true, length = 50)
    private String caseReference;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "customer_id", nullable = false)
    private Customer customer;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 30)
    private CaseStatus status;

    @Column(name = "assigned_to")
    private UUID assignedTo;

    @Column(name = "assigned_at")
    private Instant assignedAt;

    @Column(name = "started_at", nullable = false)
    private Instant startedAt;

    @Column(name = "completed_at")
    private Instant completedAt;

    @Column(name = "risk_score")
    private Integer riskScore;

    @Column(name = "decision")
    private String decision;

    @Column(name = "decision_reason", length = 1000)
    private String decisionReason;

    @Column(name = "decision_by")
    private UUID decisionBy;

    @Column(name = "decision_at")
    private Instant decisionAt;

    public boolean isActive() {
        return status != CaseStatus.CLOSED && status != CaseStatus.REJECTED;
    }

    public boolean isAssigned() {
        return assignedTo != null;
    }

    public void assign(UUID userId) {
        this.assignedTo = userId;
        this.assignedAt = Instant.now();
        if (this.status == CaseStatus.PENDING) {
            this.status = CaseStatus.IN_PROGRESS;
        }
    }

    public void complete(int riskScore) {
        this.riskScore = riskScore;
        this.completedAt = Instant.now();
        if (this.status == CaseStatus.IN_PROGRESS) {
            this.status = CaseStatus.COMPLETED;
        }
    }

    public void approve(UUID userId, String reason) {
        this.decision = "APPROVED";
        this.decisionReason = reason;
        this.decisionBy = userId;
        this.decisionAt = Instant.now();
        this.completedAt = Instant.now();
        this.status = CaseStatus.CLOSED;
    }

    public void reject(UUID userId, String reason) {
        this.decision = "REJECTED";
        this.decisionReason = reason;
        this.decisionBy = userId;
        this.decisionAt = Instant.now();
        this.completedAt = Instant.now();
        this.status = CaseStatus.REJECTED;
    }
}
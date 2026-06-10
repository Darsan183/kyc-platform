package com.kyc.platform.kycplatform.onboarding.dto;

import com.kyc.platform.kycplatform.onboarding.domain.KycCase;
import com.kyc.platform.kycplatform.onboarding.domain.enums.CaseStatus;
import lombok.*;

import java.time.Instant;
import java.util.UUID;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class KycCaseDto {

    private UUID id;
    private String caseReference;
    private UUID customerId;
    private String customerName;
    private CaseStatus status;
    private UUID assignedTo;
    private String assignedToName;
    private Instant startedAt;
    private Instant assignedAt;
    private Instant completedAt;
    private Integer riskScore;
    private String decision;
    private String decisionReason;
    private UUID decisionBy;
    private Instant decisionAt;

    public static KycCaseDto fromEntity(KycCase kycCase) {
        return KycCaseDto.builder()
                .id(kycCase.getId())
                .caseReference(kycCase.getCaseReference())
                .customerId(kycCase.getCustomer().getId())
                .customerName(kycCase.getCustomer().getFullName())
                .status(kycCase.getStatus())
                .assignedTo(kycCase.getAssignedTo())
                .startedAt(kycCase.getStartedAt())
                .assignedAt(kycCase.getAssignedAt())
                .completedAt(kycCase.getCompletedAt())
                .riskScore(kycCase.getRiskScore())
                .decision(kycCase.getDecision())
                .decisionReason(kycCase.getDecisionReason())
                .decisionBy(kycCase.getDecisionBy())
                .decisionAt(kycCase.getDecisionAt())
                .build();
    }
}
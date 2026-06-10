package com.kyc.platform.kycplatform.onboarding.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.*;

import java.util.UUID;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class KycDecisionRequest {

    @NotNull(message = "Decision by is required")
    private UUID decisionBy;

    @NotBlank(message = "Decision is required (APPROVED/REJECTED)")
    private String decision;

    private String decisionReason;
}
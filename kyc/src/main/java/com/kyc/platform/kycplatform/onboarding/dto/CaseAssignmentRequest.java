package com.kyc.platform.kycplatform.onboarding.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.*;

import java.util.UUID;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CaseAssignmentRequest {

    @NotBlank(message = "Case ID is required")
    private UUID caseId;

    private UUID assignedTo;
}
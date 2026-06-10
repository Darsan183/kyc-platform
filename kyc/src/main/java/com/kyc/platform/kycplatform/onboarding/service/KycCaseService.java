package com.kyc.platform.kycplatform.onboarding.service;

import com.kyc.platform.kycplatform.onboarding.dto.CaseAssignmentRequest;
import com.kyc.platform.kycplatform.onboarding.dto.KycCaseDto;
import com.kyc.platform.kycplatform.onboarding.dto.KycDecisionRequest;
import com.kyc.platform.kycplatform.onboarding.domain.enums.CaseStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.UUID;

public interface KycCaseService {

    KycCaseDto createCase(UUID customerId);

    KycCaseDto getCase(UUID caseId);

    KycCaseDto getCaseByReference(String caseReference);

    Page<KycCaseDto> getCasesByStatus(CaseStatus status, Pageable pageable);

    Page<KycCaseDto> getAssignedCases(UUID assignedTo, Pageable pageable);

    KycCaseDto assignCase(CaseAssignmentRequest request);

    KycCaseDto updateStatus(UUID caseId, CaseStatus status);

    KycCaseDto completeCase(UUID caseId, int riskScore);

    KycCaseDto makeDecision(UUID caseId, KycDecisionRequest request);
}
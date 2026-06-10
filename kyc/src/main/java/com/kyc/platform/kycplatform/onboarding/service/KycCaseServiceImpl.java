package com.kyc.platform.kycplatform.onboarding.service;

import com.kyc.platform.kycplatform.onboarding.domain.KycCase;
import com.kyc.platform.kycplatform.onboarding.dto.CaseAssignmentRequest;
import com.kyc.platform.kycplatform.onboarding.dto.KycCaseDto;
import com.kyc.platform.kycplatform.onboarding.dto.KycDecisionRequest;
import com.kyc.platform.kycplatform.onboarding.domain.Customer;
import com.kyc.platform.kycplatform.onboarding.domain.enums.CaseStatus;
import com.kyc.platform.kycplatform.onboarding.repository.CustomerRepository;
import com.kyc.platform.kycplatform.onboarding.repository.KycCaseRepository;
import com.kyc.platform.kycplatform.shared.exception.ResourceNotFoundException;
import com.kyc.platform.kycplatform.shared.exception.BusinessException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.Random;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class KycCaseServiceImpl implements KycCaseService {

    private final KycCaseRepository kycCaseRepository;
    private final CustomerRepository customerRepository;

    @Override
    public KycCaseDto createCase(UUID customerId) {
        Customer customer = customerRepository.findById(customerId)
                .orElseThrow(() -> new ResourceNotFoundException("Customer", customerId));

        String caseReference = generateCaseReference();

        KycCase kycCase = KycCase.builder()
                .caseReference(caseReference)
                .customer(customer)
                .status(CaseStatus.PENDING)
                .startedAt(Instant.now())
                .build();

        KycCase savedCase = kycCaseRepository.save(kycCase);
        log.info("KYC case created: {} for customer: {}", caseReference, customerId);
        
        return KycCaseDto.fromEntity(savedCase);
    }

    @Override
    @Transactional(readOnly = true)
    public KycCaseDto getCase(UUID caseId) {
        KycCase kycCase = kycCaseRepository.findById(caseId)
                .orElseThrow(() -> new ResourceNotFoundException("KYC Case", caseId));
        return KycCaseDto.fromEntity(kycCase);
    }

    @Override
    @Transactional(readOnly = true)
    public KycCaseDto getCaseByReference(String caseReference) {
        KycCase kycCase = kycCaseRepository.findByCaseReference(caseReference)
                .orElseThrow(() -> new ResourceNotFoundException("KYC Case", caseReference));
        return KycCaseDto.fromEntity(kycCase);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<KycCaseDto> getCasesByStatus(CaseStatus status, Pageable pageable) {
        return kycCaseRepository.findByStatus(status, pageable)
                .map(KycCaseDto::fromEntity);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<KycCaseDto> getAssignedCases(UUID assignedTo, Pageable pageable) {
        return kycCaseRepository.findByAssignedTo(assignedTo, pageable)
                .map(KycCaseDto::fromEntity);
    }

    @Override
    public KycCaseDto assignCase(CaseAssignmentRequest request) {
        KycCase kycCase = kycCaseRepository.findById(request.getCaseId())
                .orElseThrow(() -> new ResourceNotFoundException("KYC Case", request.getCaseId()));

        if (!kycCase.isActive()) {
            throw new BusinessException("CASE_NOT_ACTIVE", 
                    "Cannot assign closed or rejected case");
        }

        UUID assignee = request.getAssignedTo() != null ? request.getAssignedTo() : null;
        kycCase.assign(assignee);
        
        KycCase updatedCase = kycCaseRepository.save(kycCase);
        log.info("KYC case {} assigned to {}", kycCase.getCaseReference(), assignee);
        
        return KycCaseDto.fromEntity(updatedCase);
    }

    @Override
    public KycCaseDto updateStatus(UUID caseId, CaseStatus status) {
        KycCase kycCase = kycCaseRepository.findById(caseId)
                .orElseThrow(() -> new ResourceNotFoundException("KYC Case", caseId));

        kycCase.setStatus(status);
        KycCase updatedCase = kycCaseRepository.save(kycCase);
        
        return KycCaseDto.fromEntity(updatedCase);
    }

    @Override
    public KycCaseDto completeCase(UUID caseId, int riskScore) {
        KycCase kycCase = kycCaseRepository.findById(caseId)
                .orElseThrow(() -> new ResourceNotFoundException("KYC Case", caseId));

        if (kycCase.getStatus() != CaseStatus.REVIEW) {
            throw new BusinessException("INVALID_STATE", 
                    "Case must be in REVIEW status to complete");
        }

        kycCase.complete(riskScore);
        KycCase updatedCase = kycCaseRepository.save(kycCase);
        
        return KycCaseDto.fromEntity(updatedCase);
    }

    @Override
    public KycCaseDto makeDecision(UUID caseId, KycDecisionRequest request) {
        KycCase kycCase = kycCaseRepository.findById(caseId)
                .orElseThrow(() -> new ResourceNotFoundException("KYC Case", caseId));

        if (kycCase.getStatus() != CaseStatus.COMPLETED) {
            throw new BusinessException("INVALID_STATE", 
                    "Case must be in COMPLETED status to make decision");
        }

        if ("APPROVED".equalsIgnoreCase(request.getDecision())) {
            kycCase.approve(request.getDecisionBy(), request.getDecisionReason());
        } else if ("REJECTED".equalsIgnoreCase(request.getDecision())) {
            kycCase.reject(request.getDecisionBy(), request.getDecisionReason());
        } else {
            throw new BusinessException("INVALID_DECISION", 
                    "Decision must be APPROVED or REJECTED");
        }

        KycCase updatedCase = kycCaseRepository.save(kycCase);
        log.info("Decision made for case {}: {}", kycCase.getCaseReference(), request.getDecision());
        
        return KycCaseDto.fromEntity(updatedCase);
    }

    private String generateCaseReference() {
        String timestamp = String.valueOf(System.currentTimeMillis() % 1000000);
        int random = new Random().nextInt(1000);
        return "KYC-" + timestamp + "-" + String.format("%03d", random);
    }
}
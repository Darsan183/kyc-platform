package com.kyc.platform.kycplatform.onboarding.service;

import com.kyc.platform.kycplatform.onboarding.domain.Customer;
import com.kyc.platform.kycplatform.onboarding.domain.KycCase;
import com.kyc.platform.kycplatform.onboarding.dto.CaseAssignmentRequest;
import com.kyc.platform.kycplatform.onboarding.dto.KycDecisionRequest;
import com.kyc.platform.kycplatform.onboarding.domain.enums.CaseStatus;
import com.kyc.platform.kycplatform.onboarding.repository.CustomerRepository;
import com.kyc.platform.kycplatform.onboarding.repository.KycCaseRepository;
import com.kyc.platform.kycplatform.shared.exception.BusinessException;
import com.kyc.platform.kycplatform.shared.exception.ResourceNotFoundException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class KycCaseServiceTest {

    @Mock
    private KycCaseRepository kycCaseRepository;

    @Mock
    private CustomerRepository customerRepository;

    @InjectMocks
    private KycCaseServiceImpl kycCaseService;

    private Customer testCustomer;
    private UUID customerId;
    private UUID caseId;

    @BeforeEach
    void setUp() {
        customerId = UUID.randomUUID();
        caseId = UUID.randomUUID();
        
        testCustomer = Customer.builder()
                .id(customerId)
                .firstName("John")
                .lastName("Doe")
                .customerReference("CUST-001")
                .build();
    }

    @Test
    void shouldCreateCaseSuccessfully() {
        when(customerRepository.findById(customerId)).thenReturn(Optional.of(testCustomer));
        when(kycCaseRepository.save(any())).thenAnswer(inv -> {
            KycCase c = inv.getArgument(0);
            c.setId(caseId);
            return c;
        });

        var result = kycCaseService.createCase(customerId);

        assertNotNull(result);
        assertEquals(CaseStatus.PENDING, result.getStatus());
        assertNotNull(result.getCaseReference());
    }

    @Test
    void shouldAssignCaseSuccessfully() {
        UUID analystId = UUID.randomUUID();
        
        KycCase kycCase = KycCase.builder()
                .id(caseId)
                .status(CaseStatus.PENDING)
                .build();
        
        CaseAssignmentRequest request = new CaseAssignmentRequest();
        request.setCaseId(caseId);
        request.setAssignedTo(analystId);

        when(kycCaseRepository.findById(caseId)).thenReturn(Optional.of(kycCase));
        when(kycCaseRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        var result = kycCaseService.assignCase(request);

        assertEquals(analystId, kycCase.getAssignedTo());
    }

    @Test
    void shouldCompleteCaseSuccessfully() {
        KycCase kycCase = KycCase.builder()
                .id(caseId)
                .status(CaseStatus.REVIEW)
                .build();

        when(kycCaseRepository.findById(caseId)).thenReturn(Optional.of(kycCase));
        when(kycCaseRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        var result = kycCaseService.completeCase(caseId, 35);

        assertEquals(35, kycCase.getRiskScore());
        assertEquals(CaseStatus.COMPLETED, kycCase.getStatus());
    }

    @Test
    void shouldRejectCompleteInInvalidState() {
        KycCase kycCase = KycCase.builder()
                .id(caseId)
                .status(CaseStatus.PENDING)
                .build();

        when(kycCaseRepository.findById(caseId)).thenReturn(Optional.of(kycCase));

        assertThrows(BusinessException.class, 
                () -> kycCaseService.completeCase(caseId, 35));
    }

    @Test
    void shouldApproveCase() {
        KycCase kycCase = KycCase.builder()
                .id(caseId)
                .status(CaseStatus.COMPLETED)
                .build();
        
        UUID approverId = UUID.randomUUID();
        KycDecisionRequest request = KycDecisionRequest.builder()
                .decisionBy(approverId)
                .decision("APPROVED")
                .decisionReason("All checks passed")
                .build();

        when(kycCaseRepository.findById(caseId)).thenReturn(Optional.of(kycCase));
        when(kycCaseRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        var result = kycCaseService.makeDecision(caseId, request);

        assertEquals("APPROVED", kycCase.getDecision());
        assertEquals(CaseStatus.CLOSED, kycCase.getStatus());
    }
}
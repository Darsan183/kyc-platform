package com.kyc.platform.kycplatform.document;

import com.kyc.platform.kycplatform.document.domain.enums.DocumentType;
import com.kyc.platform.kycplatform.document.dto.DocumentDto;
import com.kyc.platform.kycplatform.document.repository.DocumentRepository;
import com.kyc.platform.kycplatform.document.service.DocumentService;
import com.kyc.platform.kycplatform.onboarding.domain.Customer;
import com.kyc.platform.kycplatform.onboarding.domain.KycCase;
import com.kyc.platform.kycplatform.onboarding.domain.enums.CaseStatus;
import com.kyc.platform.kycplatform.onboarding.repository.CustomerRepository;
import com.kyc.platform.kycplatform.onboarding.repository.KycCaseRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
@Transactional
class DocumentProcessingIntegrationTest {

    @Autowired
    private DocumentService documentService;

    @Autowired
    private DocumentRepository documentRepository;

    @Autowired
    private CustomerRepository customerRepository;

    @Autowired
    private KycCaseRepository kycCaseRepository;

    private UUID customerId;
    private UUID caseId;

    @BeforeEach
    void setUp() {
        // Create test customer
        Customer customer = Customer.builder()
                .customerReference("TEST-CUST-001")
                .firstName("Test")
                .lastName("Customer")
                .email("test@example.com")
                .phone("+1234567890")
                .dateOfBirth(LocalDate.of(1990, 1, 1))
                .country("US")
                .build();
        customer = customerRepository.save(customer);
        customerId = customer.getId();

        // Create test case
        KycCase kycCase = KycCase.builder()
                .caseReference("KYC-001")
                .customer(customer)
                .status(CaseStatus.PENDING)
                .build();
        kycCase = kycCaseRepository.save(kycCase);
        caseId = kycCase.getId();
    }

    @Test
    void shouldUploadDocument() {
        MockMultipartFile file = new MockMultipartFile(
                "file",
                "passport.pdf",
                "application/pdf",
                "test content".getBytes()
        );

        DocumentDto result = documentService.uploadDocument(caseId, DocumentType.PASSPORT, file);

        assertNotNull(result);
        assertNotNull(result.getId());
        assertEquals(DocumentType.PASSPORT, result.getType());
        assertEquals(caseId, result.getCaseId());
    }

    @Test
    void shouldGetDocumentByCase() {
        MockMultipartFile file = new MockMultipartFile(
                "file",
                "aadhaar.jpg",
                "image/jpeg",
                "test content".getBytes()
        );

        documentService.uploadDocument(caseId, DocumentType.AADHAAR, file);
        var result = documentService.getDocumentsByCase(caseId, null);

        assertNotNull(result);
    }
}
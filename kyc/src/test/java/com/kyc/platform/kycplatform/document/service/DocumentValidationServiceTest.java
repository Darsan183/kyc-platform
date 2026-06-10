package com.kyc.platform.kycplatform.document.service;

import com.kyc.platform.kycplatform.document.dto.ExtractedData;
import com.kyc.platform.kycplatform.document.domain.enums.DocumentType;
import com.kyc.platform.kycplatform.document.service.impl.DocumentValidationServiceImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.LocalDate;

import static org.junit.jupiter.api.Assertions.*;

class DocumentValidationServiceTest {

    private DocumentValidationServiceImpl validationService;

    @BeforeEach
    void setUp() {
        validationService = new DocumentValidationServiceImpl();
    }

    @Test
    void shouldValidateValidPassport() {
        ExtractedData data = ExtractedData.builder()
                .passportNumber("A12345678")
                .expiryDate(LocalDate.now().plusYears(5))
                .build();

        var result = validationService.validateDocument(data, DocumentType.PASSPORT);
        assertTrue(result.valid());
    }

    @Test
    void shouldRejectInvalidPassport() {
        ExtractedData data = ExtractedData.builder()
                .passportNumber("A1")
                .build();

        var result = validationService.validateDocument(data, DocumentType.PASSPORT);
        assertFalse(result.valid());
        assertEquals("passportNumber", result.field());
    }

    @Test
    void shouldValidateValidAadhaar() {
        ExtractedData data = ExtractedData.builder()
                .aadhaarNumber("1234-5678-9012")
                .build();

        var result = validationService.validateDocument(data, DocumentType.AADHAAR);
        assertTrue(result.valid());
    }

    @Test
    void shouldRejectInvalidAadhaar() {
        ExtractedData data = ExtractedData.builder()
                .aadhaarNumber("123")
                .build();

        var result = validationService.validateDocument(data, DocumentType.AADHAAR);
        assertFalse(result.valid());
        assertEquals("aadhaarNumber", result.field());
    }

    @Test
    void shouldValidateValidPan() {
        ExtractedData data = ExtractedData.builder()
                .panNumber("ABCDE1234F")
                .build();

        var result = validationService.validateDocument(data, DocumentType.PAN);
        assertTrue(result.valid());
    }

    @Test
    void shouldValidateUtilityBill() {
        ExtractedData data = ExtractedData.builder()
                .providerName("Electric Company")
                .billDate("2024-01-15")
                .build();

        var result = validationService.validateDocument(data, DocumentType.UTILITY_BILL);
        assertTrue(result.valid());
    }
}
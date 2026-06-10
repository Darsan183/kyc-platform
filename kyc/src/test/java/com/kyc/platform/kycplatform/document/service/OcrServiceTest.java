package com.kyc.platform.kycplatform.document.service;

import com.kyc.platform.kycplatform.document.dto.ExtractedData;
import com.kyc.platform.kycplatform.document.domain.enums.DocumentType;
import com.kyc.platform.kycplatform.document.service.impl.OcrServiceImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.io.ByteArrayInputStream;
import java.time.LocalDate;

import static org.junit.jupiter.api.Assertions.*;

class OcrServiceTest {

    private OcrServiceImpl ocrService;
    private ByteArrayInputStream testStream;

    @BeforeEach
    void setUp() {
        ocrService = new OcrServiceImpl();
        testStream = new ByteArrayInputStream("test document content".getBytes());
    }

    @Test
    void shouldExtractPassportData() {
        ExtractedData data = ocrService.extractData(testStream, DocumentType.PASSPORT, "application/pdf");
        
        assertNotNull(data);
        assertNotNull(data.getPassportNumber());
        assertEquals(1, ocrService.getPageCount());
        assertTrue(ocrService.getConfidenceScore() >= 0.7);
    }

    @Test
    void shouldExtractAadhaarData() {
        ExtractedData data = ocrService.extractData(testStream, DocumentType.AADHAAR, "image/jpeg");
        
        assertNotNull(data);
        assertNotNull(data.getAadhaarNumber());
        assertEquals(1, ocrService.getPageCount());
    }

    @Test
    void shouldExtractPanData() {
        ExtractedData data = ocrService.extractData(testStream, DocumentType.PAN, "image/png");
        
        assertNotNull(data);
        assertNotNull(data.getPanNumber());
    }
}
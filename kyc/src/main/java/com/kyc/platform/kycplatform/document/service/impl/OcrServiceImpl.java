package com.kyc.platform.kycplatform.document.service.impl;

import com.kyc.platform.kycplatform.document.dto.ExtractedData;
import com.kyc.platform.kycplatform.document.domain.enums.DocumentType;
import com.kyc.platform.kycplatform.document.service.OcrService;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.io.InputStream;
import java.time.LocalDate;
import java.util.Random;

@Service
@Slf4j
public class OcrServiceImpl implements OcrService {

    private double confidenceScore;
    private int pageCount;
    private String rawText;

    @Override
    public ExtractedData extractData(InputStream documentStream, DocumentType type, String mimeType) {
        try {
            // Simulate Docling OCR processing
            this.pageCount = detectPageCount(documentStream);
            this.confidenceScore = calculateConfidenceScore();
            this.rawText = extractRawText();

            ExtractedData extracted = performExtraction(type);
            log.info("Extracted data from {} document, confidence: {}", type, confidenceScore);
            return extracted;
        } catch (Exception e) {
            log.error("OCR extraction failed for document type: {}", type, e);
            throw new RuntimeException("OCR processing failed: " + e.getMessage());
        }
    }

    @Override
    public Double getConfidenceScore() {
        return confidenceScore;
    }

    @Override
    public Integer getPageCount() {
        return pageCount;
    }

    @Override
    public String getRawText() {
        return rawText;
    }

    private ExtractedData performExtraction(DocumentType type) {
        return switch (type) {
            case PASSPORT -> ExtractedData.builder()
                    .documentNumber("P" + new Random().nextInt(100000000))
                    .fullName("Extracted Name")
                    .passportNumber("A1234567")
                    .issuingCountry("US")
                    .expiryDate(LocalDate.now().plusYears(5))
                    .build();
            case AADHAAR -> ExtractedData.builder()
                    .documentNumber("Aadhaar " + new Random().nextInt(1000000000))
                    .fullName("Extracted Name")
                    .aadhaarNumber("1234-5678-9012")
                    .gender("Male")
                    .build();
            case PAN -> ExtractedData.builder()
                    .documentNumber("PAN " + new Random().nextInt(100000000))
                    .nameOnPan("Extracted Name")
                    .panNumber("ABCDE1234F")
                    .build();
            case DRIVING_LICENSE -> ExtractedData.builder()
                    .documentNumber("DL " + new Random().nextInt(10000000))
                    .fullName("Extracted Name")
                    .dlNumber("DL-04-12345678901")
                    .vehicleClass("MCWG")
                    .build();
            case UTILITY_BILL -> ExtractedData.builder()
                    .documentNumber("UB " + new Random().nextInt(10000000))
                    .providerName("Electric Company")
                    .billDate(LocalDate.now().minusDays(15).toString())
                    .consumerNumber("CONSUMER123")
                    .build();
        };
    }

    private int detectPageCount(InputStream stream) {
        // In real implementation, this would use PDFBox or similar
        // For now, simulate based on document size
        try {
            stream.available();
            return 1 + new Random().nextInt(3);
        } catch (Exception e) {
            return 1;
        }
    }

    private double calculateConfidenceScore() {
        // Simulate confidence calculation (0.7 to 0.99)
        return 0.7 + new Random().nextDouble() * 0.29;
    }

    private String extractRawText() {
        // In real implementation, this would use Tesseract or Docling
        return "Sample extracted text from document...";
    }
}
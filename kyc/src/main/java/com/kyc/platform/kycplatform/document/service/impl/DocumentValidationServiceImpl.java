package com.kyc.platform.kycplatform.document.service.impl;

import com.kyc.platform.kycplatform.document.dto.ExtractedData;
import com.kyc.platform.kycplatform.document.domain.enums.DocumentType;
import com.kyc.platform.kycplatform.document.service.DocumentValidationService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Service
@Slf4j
public class DocumentValidationServiceImpl implements DocumentValidationService {

    private static final int MIN_CONFIDENCE_THRESHOLD = 80;

    @Override
    public ValidationResult validateDocument(ExtractedData data, DocumentType type) {
        return switch (type) {
            case PASSPORT -> validatePassport(data);
            case AADHAAR -> validateAadhaar(data);
            case PAN -> validatePan(data);
            case DRIVING_LICENSE -> validateDrivingLicense(data);
            case UTILITY_BILL -> validateUtilityBill(data);
        };
    }

    private ValidationResult validatePassport(ExtractedData data) {
        if (data.getPassportNumber() == null || data.getPassportNumber().length() < 6) {
            return new ValidationResult(false, "Invalid passport number", "passportNumber");
        }
        if (data.getExpiryDate() != null && data.getExpiryDate().isBefore(java.time.LocalDate.now())) {
            return new ValidationResult(false, "Passport expired", "expiryDate");
        }
        return ValidationResult.valid();
    }

    private ValidationResult validateAadhaar(ExtractedData data) {
        if (data.getAadhaarNumber() == null || !data.getAadhaarNumber().matches("\\d{4}-\\d{4}-\\d{4}")) {
            return new ValidationResult(false, "Invalid Aadhaar number format", "aadhaarNumber");
        }
        return ValidationResult.valid();
    }

    private ValidationResult validatePan(ExtractedData data) {
        if (data.getPanNumber() == null || !data.getPanNumber().matches("[A-Z]{5}\\d{4}[A-Z]")) {
            return new ValidationResult(false, "Invalid PAN format", "panNumber");
        }
        return ValidationResult.valid();
    }

    private ValidationResult validateDrivingLicense(ExtractedData data) {
        if (data.getDlNumber() == null || data.getDlNumber().length() < 5) {
            return new ValidationResult(false, "Invalid driving license number", "dlNumber");
        }
        return ValidationResult.valid();
    }

    private ValidationResult validateUtilityBill(ExtractedData data) {
        if (data.getProviderName() == null || data.getProviderName().isBlank()) {
            return new ValidationResult(false, "Provider name required", "providerName");
        }
        if (data.getBillDate() == null || data.getBillDate().isBlank()) {
            return new ValidationResult(false, "Bill date required", "billDate");
        }
        return ValidationResult.valid();
    }
}
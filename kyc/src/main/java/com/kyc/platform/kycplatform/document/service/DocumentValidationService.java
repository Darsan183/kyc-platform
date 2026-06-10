package com.kyc.platform.kycplatform.document.service;

import com.kyc.platform.kycplatform.document.dto.ExtractedData;
import com.kyc.platform.kycplatform.document.domain.enums.DocumentType;

public interface DocumentValidationService {

    ValidationResult validateDocument(ExtractedData data, DocumentType type);

    record ValidationResult(boolean valid, String message, String field) {}
}
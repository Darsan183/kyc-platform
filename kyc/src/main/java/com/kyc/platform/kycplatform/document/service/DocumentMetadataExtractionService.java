package com.kyc.platform.kycplatform.document.service;

import com.kyc.platform.kycplatform.document.dto.ExtractedData;
import com.kyc.platform.kycplatform.document.dto.DocumentMetadata;
import com.kyc.platform.kycplatform.document.domain.enums.DocumentType;

import java.io.InputStream;

public interface DocumentMetadataExtractionService {

    DocumentMetadata extractMetadata(InputStream documentStream, DocumentType type);

    ExtractedData getExtractedData(String extractedJson);
}
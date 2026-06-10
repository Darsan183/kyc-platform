package com.kyc.platform.kycplatform.document.service;

import com.kyc.platform.kycplatform.document.dto.ExtractedData;
import com.kyc.platform.kycplatform.document.domain.enums.DocumentType;

import java.io.InputStream;

public interface OcrService {

    ExtractedData extractData(InputStream documentStream, DocumentType type, String mimeType);

    Double getConfidenceScore();

    Integer getPageCount();

    String getRawText();
}
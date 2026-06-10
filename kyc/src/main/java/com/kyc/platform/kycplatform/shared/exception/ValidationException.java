package com.kyc.platform.kycplatform.shared.exception;

public class ValidationException extends BaseException {
    
    public ValidationException(String message) {
        super("VALIDATION_ERROR", message);
    }

    public ValidationException(String message, Object... params) {
        super("VALIDATION_ERROR", message, params);
    }

    public ValidationException(String field, String message) {
        super("VALIDATION_ERROR", message + ": " + field);
    }
}
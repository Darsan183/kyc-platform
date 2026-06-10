package com.kyc.platform.kycplatform.shared.exception;

public class ResourceNotFoundException extends BusinessException {
    
    public ResourceNotFoundException(String resource, Object identifier) {
        super("RESOURCE_NOT_FOUND", 
            String.format("%s not found with identifier: %s", resource, identifier));
    }

    public ResourceNotFoundException(String resource, String field, Object value) {
        super("RESOURCE_NOT_FOUND",
            String.format("%s not found with %s: %s", resource, field, value));
    }
}
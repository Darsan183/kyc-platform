package com.kyc.platform.kycplatform.shared.exception;

public class BusinessException extends BaseException {
    
    public BusinessException(String errorCode, String message) {
        super(errorCode, message);
    }

    public BusinessException(String errorCode, String message, Object... params) {
        super(errorCode, message, params);
    }

    public BusinessException(String errorCode, String message, Throwable cause) {
        super(errorCode, message, cause);
    }

    public BusinessException(String errorCode, String message, Throwable cause, Object... params) {
        super(errorCode, message, cause, params);
    }
}
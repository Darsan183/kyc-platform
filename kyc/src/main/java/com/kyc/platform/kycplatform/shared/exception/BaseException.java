package com.kyc.platform.kycplatform.shared.exception;

import lombok.Getter;

@Getter
public abstract class BaseException extends RuntimeException {
    
    private final String errorCode;
    private final String message;
    private final Object[] params;

    protected BaseException(String errorCode, String message, Object... params) {
        super(message, null, true, false);
        this.errorCode = errorCode;
        this.message = message;
        this.params = params != null ? params : new Object[0];
    }

    protected BaseException(String errorCode, String message, Throwable cause, Object... params) {
        super(message, cause, true, false);
        this.errorCode = errorCode;
        this.message = message;
        this.params = params != null ? params : new Object[0];
    }
}
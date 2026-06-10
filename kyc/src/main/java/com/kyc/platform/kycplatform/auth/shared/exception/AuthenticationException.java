package com.kyc.platform.kycplatform.auth.shared.exception;

import com.kyc.platform.kycplatform.shared.exception.BusinessException;

public class AuthenticationException extends BusinessException {

    public AuthenticationException(String message) {
        super("AUTHENTICATION_ERROR", message);
    }

    public AuthenticationException(String message, Object... params) {
        super("AUTHENTICATION_ERROR", message, params);
    }
}
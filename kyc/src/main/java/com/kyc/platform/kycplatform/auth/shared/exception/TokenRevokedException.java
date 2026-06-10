package com.kyc.platform.kycplatform.auth.shared.exception;

import com.kyc.platform.kycplatform.shared.exception.BusinessException;

public class TokenRevokedException extends BusinessException {

    public TokenRevokedException(String message) {
        super("TOKEN_REVOKED", message);
    }

    public TokenRevokedException(String message, Object... params) {
        super("TOKEN_REVOKED", message, params);
    }
}
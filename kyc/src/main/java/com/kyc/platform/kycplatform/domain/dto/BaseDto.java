package com.kyc.platform.kycplatform.domain.dto;

import jakarta.validation.constraints.NotNull;
import java.util.UUID;

public record BaseDto(@NotNull UUID id) {}

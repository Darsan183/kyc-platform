package com.kyc.platform.kycplatform.domain;

import jakarta.persistence.MappedSuperclass;
import jakarta.persistence.Version;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@MappedSuperclass
public abstract class BaseEntityWithVersion extends BaseEntity {

    @Version
    private Long version;
}
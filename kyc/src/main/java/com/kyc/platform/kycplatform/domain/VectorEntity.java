package com.kyc.platform.kycplatform.domain;

import jakarta.persistence.MappedSuperclass;
import org.hibernate.annotations.Array;

import java.util.List;

@MappedSuperclass
public abstract class VectorEntity extends BaseEntity {
    
    // Vector storage will be handled in concrete entities
    // This provides the base for pgvector integration
}
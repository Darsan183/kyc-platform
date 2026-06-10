package com.kyc.platform.kycplatform.onboarding.domain;

import com.kyc.platform.kycplatform.domain.BaseEntity;
import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "customer_profiles")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CustomerProfile extends BaseEntity {

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "customer_id", nullable = false, unique = true)
    private Customer customer;

    @Column(name = "occupation", length = 100)
    private String occupation;

    @Column(name = "employer_name", length = 255)
    private String employerName;

    @Column(name = "annual_income", precision = 19, scale = 2)
    private BigDecimal annualIncome;

    @Column(name = "source_of_funds", length = 500)
    private String sourceOfFunds;

    @Column(name = "expected_transaction_volume", precision = 19, scale = 2)
    private BigDecimal expectedTransactionVolume;

    @Column(name = "pep_status")
    private boolean pepStatus;

    @Column(name = "pep_details", length = 500)
    private String pepDetails;

    @Column(name = "risk_rating", length = 20)
    private String riskRating;

    @Column(name = "last_verified_at")
    private Instant lastVerifiedAt;

    public void markVerified() {
        this.lastVerifiedAt = Instant.now();
    }
}
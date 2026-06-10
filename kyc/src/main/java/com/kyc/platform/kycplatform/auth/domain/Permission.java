package com.kyc.platform.kycplatform.auth.domain;

import com.kyc.platform.kycplatform.domain.BaseEntity;
import jakarta.persistence.*;
import lombok.*;

import java.util.HashSet;
import java.util.Set;

@Entity
@Table(name = "permissions")
@Getter
@Setter
@ToString(exclude = "roles")
@EqualsAndHashCode(exclude = "roles", callSuper = true)
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Permission extends BaseEntity {

    @Column(name = "name", nullable = false, unique = true, length = 100)
    private String name;

    @Column(name = "description", length = 255)
    private String description;

    @ManyToMany(mappedBy = "permissions", fetch = FetchType.LAZY)
    @Builder.Default
    private Set<Role> roles = new HashSet<>();

    public enum PermissionName {
        // User Management
        USER_READ("user:read"),
        USER_WRITE("user:write"),
        USER_DELETE("user:delete"),
        
        // Customer Management
        CUSTOMER_READ("customer:read"),
        CUSTOMER_WRITE("customer:write"),
        CUSTOMER_DELETE("customer:delete"),
        
        // Case Management
        CASE_READ("case:read"),
        CASE_WRITE("case:write"),
        CASE_APPROVE("case:approve"),
        
        // Document Management
        DOCUMENT_READ("document:read"),
        DOCUMENT_WRITE("document:write"),
        
        // AML Screening
        AML_SCREEN("aml:screen"),
        AML_READ("aml:read"),
        
        // Risk Management
        RISK_READ("risk:read"),
        RISK_WRITE("risk:write"),
        
        // Audit
        AUDIT_READ("audit:read"),
        AUDIT_EXPORT("audit:export"),
        
        // System
        SYSTEM_CONFIG("system:config"),
        SYSTEM_MONITOR("system:monitor");

        private final String value;

        PermissionName(String value) {
            this.value = value;
        }

        public String getValue() {
            return value;
        }
    }
}
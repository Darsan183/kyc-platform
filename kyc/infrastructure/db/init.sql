-- Initialize KYC Platform database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Customers table (already created via Flyway V3__onboarding_tables.sql)
-- Users table (already created via Flyway V2__auth_tables.sql)
-- Documents table (already created via Flyway V4__document_tables.sql)

-- Additional indexes for performance
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status);
CREATE INDEX IF NOT EXISTS idx_documents_case_id ON documents(kyc_case_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(verification_status);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID,
    user_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_user ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created ON audit_log(created_at DESC);
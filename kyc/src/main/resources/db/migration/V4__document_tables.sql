-- Documents table migration
-- Version: V4__document_tables.sql

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_reference VARCHAR(50) NOT NULL UNIQUE,
    case_id UUID NOT NULL,
    type VARCHAR(30) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    original_file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_size BIGINT NOT NULL,
    hash VARCHAR(64),
    verification_status VARCHAR(30) NOT NULL,
    verified_at TIMESTAMP WITH TIME ZONE,
    verification_notes VARCHAR(1000),
    extracted_data JSONB,
    ocr_confidence_score DOUBLE PRECISION,
    page_count INTEGER,
    version BIGINT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    FOREIGN KEY (case_id) REFERENCES kyc_cases(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_documents_ref ON documents(document_reference);
CREATE INDEX idx_documents_case ON documents(case_id);
CREATE INDEX idx_documents_type ON documents(type);
CREATE INDEX idx_documents_status ON documents(verification_status);
CREATE INDEX idx_documents_verified ON documents(verified_at);
CREATE INDEX idx_documents_file_path ON documents(file_path);
CREATE INDEX idx_documents_hash ON documents(hash);
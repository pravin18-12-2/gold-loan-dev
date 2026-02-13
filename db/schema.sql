-- Control plane: tenant registry only (no customer/loan data)
CREATE TABLE IF NOT EXISTS tenant (
  id UUID PRIMARY KEY,
  bank_name VARCHAR(255) NOT NULL,
  tenant_type VARCHAR(20) CHECK (tenant_type IN ('SHARED','DEDICATED')),
  db_host VARCHAR(255),
  db_port INTEGER,
  db_name VARCHAR(255),
  db_user VARCHAR(255),
  db_password_enc TEXT,
  schema_version VARCHAR(20),
  status VARCHAR(20) CHECK (status IN ('ACTIVE','SUSPENDED')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data plane core
CREATE TABLE IF NOT EXISTS bank (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  bank_code VARCHAR(50) UNIQUE NOT NULL,
  bank_name VARCHAR(255) NOT NULL,
  headquarters_address TEXT,
  email VARCHAR(255),
  phone VARCHAR(20),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_bank_tenant ON bank(tenant_id);

CREATE TABLE IF NOT EXISTS branch (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  bank_id UUID REFERENCES bank(id),
  branch_code VARCHAR(50),
  branch_name VARCHAR(255),
  address TEXT,
  city VARCHAR(100),
  state VARCHAR(100),
  pincode VARCHAR(20),
  manager_name VARCHAR(255),
  contact_no VARCHAR(20),
  email VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_branch_tenant ON branch(tenant_id);

CREATE TABLE IF NOT EXISTS user_account (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  phone VARCHAR(20),
  password_hash TEXT NOT NULL,
  role VARCHAR(30) CHECK (role IN ('SUPER_ADMIN','BANK_ADMIN','BRANCH_ADMIN','APPRAISER')),
  bank_id UUID,
  branch_id UUID,
  is_active BOOLEAN DEFAULT TRUE,
  last_login TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_user_tenant ON user_account(tenant_id);

CREATE TABLE IF NOT EXISTS appraiser (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  user_id UUID REFERENCES user_account(id),
  appraiser_code VARCHAR(50) UNIQUE,
  face_image_id UUID,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_appraiser_tenant ON appraiser(tenant_id);

CREATE TABLE IF NOT EXISTS customer (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  customer_code VARCHAR(50) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  face_image_id UUID,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_customer_tenant ON customer(tenant_id);

CREATE TABLE IF NOT EXISTS loan (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  loan_number VARCHAR(50) UNIQUE NOT NULL,
  customer_id UUID REFERENCES customer(id),
  appraiser_id UUID REFERENCES appraiser(id),
  bank_id UUID REFERENCES bank(id),
  branch_id UUID REFERENCES branch(id),
  status VARCHAR(30) DEFAULT 'CREATED' CHECK (status IN ('CREATED','COMPLIANCE_CAPTURED','PURITY_TESTED','COMPLETED')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  completed_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_loan_tenant ON loan(tenant_id);
CREATE INDEX IF NOT EXISTS idx_loan_status ON loan(status);

CREATE TABLE IF NOT EXISTS rbi_compliance (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  loan_id UUID REFERENCES loan(id),
  total_jewel_count INTEGER NOT NULL,
  overall_image_id UUID,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_compliance_tenant ON rbi_compliance(tenant_id);

CREATE TABLE IF NOT EXISTS rbi_compliance_item (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  compliance_id UUID REFERENCES rbi_compliance(id),
  jewel_index INTEGER NOT NULL,
  jewel_image_id UUID NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_compliance_item_tenant ON rbi_compliance_item(tenant_id);

CREATE TABLE IF NOT EXISTS purity_test (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  loan_id UUID REFERENCES loan(id),
  jewel_index INTEGER NOT NULL,
  rubbing_stone_detected BOOLEAN,
  rubbing_detected BOOLEAN,
  acid_detected BOOLEAN,
  result VARCHAR(10) CHECK (result IN ('PASS','FAIL')),
  confidence_score NUMERIC(5,2),
  ai_signature TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_purity_tenant ON purity_test(tenant_id);

CREATE TABLE IF NOT EXISTS image (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  s3_bucket VARCHAR(255),
  s3_key TEXT NOT NULL,
  file_hash VARCHAR(255),
  file_size BIGINT,
  mime_type VARCHAR(100),
  image_type VARCHAR(30) CHECK (image_type IN ('APPRAISER_FACE','CUSTOMER_FACE','JEWEL','OVERALL')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_image_tenant ON image(tenant_id);

CREATE TABLE IF NOT EXISTS loan_summary (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  loan_id UUID UNIQUE REFERENCES loan(id),
  snapshot_json JSONB NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_summary_tenant ON loan_summary(tenant_id);

CREATE TABLE IF NOT EXISTS audit_log (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  actor_user_id UUID,
  action VARCHAR(100),
  entity_type VARCHAR(50),
  entity_id UUID,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_audit_tenant ON audit_log(tenant_id);

-- Idempotency storage
CREATE TABLE IF NOT EXISTS idempotency_record (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  key VARCHAR(255) NOT NULL,
  endpoint VARCHAR(255) NOT NULL,
  response_hash VARCHAR(255) NOT NULL,
  response_payload JSONB NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (tenant_id, key, endpoint)
);
CREATE INDEX IF NOT EXISTS idx_idempotency_tenant ON idempotency_record(tenant_id);

-- Enforce immutable completed loans
CREATE OR REPLACE FUNCTION prevent_completed_loan_update()
RETURNS TRIGGER AS $$
BEGIN
  IF OLD.status = 'COMPLETED' THEN
    RAISE EXCEPTION 'Loan % is completed and immutable', OLD.id;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_prevent_completed_loan_update ON loan;
CREATE TRIGGER trg_prevent_completed_loan_update
BEFORE UPDATE ON loan
FOR EACH ROW
EXECUTE FUNCTION prevent_completed_loan_update();


-- Validate jewel item count equals total_jewel_count
CREATE OR REPLACE FUNCTION validate_compliance_item_count()
RETURNS TRIGGER AS $$
DECLARE
  item_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO item_count
  FROM rbi_compliance_item
  WHERE compliance_id = NEW.id;

  IF item_count <> NEW.total_jewel_count THEN
    RAISE EXCEPTION 'Compliance % expected % items but found %', NEW.id, NEW.total_jewel_count, item_count;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_validate_compliance_item_count ON rbi_compliance;
CREATE CONSTRAINT TRIGGER trg_validate_compliance_item_count
AFTER INSERT OR UPDATE ON rbi_compliance
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION validate_compliance_item_count();

-- Append-only enforcement for purity_test and loan_summary
CREATE OR REPLACE FUNCTION prevent_mutation_on_append_only_tables()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'Table % is append-only; % is not allowed', TG_TABLE_NAME, TG_OP;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_no_update_delete_purity_test ON purity_test;
CREATE TRIGGER trg_no_update_delete_purity_test
BEFORE UPDATE OR DELETE ON purity_test
FOR EACH ROW
EXECUTE FUNCTION prevent_mutation_on_append_only_tables();

DROP TRIGGER IF EXISTS trg_no_update_delete_loan_summary ON loan_summary;
CREATE TRIGGER trg_no_update_delete_loan_summary
BEFORE UPDATE OR DELETE ON loan_summary
FOR EACH ROW
EXECUTE FUNCTION prevent_mutation_on_append_only_tables();

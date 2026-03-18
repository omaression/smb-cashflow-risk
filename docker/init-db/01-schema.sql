-- Auto-applied on first Postgres container start.
-- Source: sql/schema.sql (symlinked conceptually; kept as copy for Docker context)

CREATE TABLE customer (
    id UUID PRIMARY KEY,
    external_customer_id TEXT UNIQUE,
    name TEXT NOT NULL,
    industry TEXT,
    segment TEXT,
    country TEXT,
    payment_terms_days INTEGER CHECK (payment_terms_days >= 0),
    credit_limit NUMERIC(14,2) CHECK (credit_limit >= 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE invoice (
    id UUID PRIMARY KEY,
    external_invoice_id TEXT UNIQUE,
    customer_id UUID NOT NULL REFERENCES customer(id),
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    currency CHAR(3) NOT NULL,
    subtotal_amount NUMERIC(14,2) NOT NULL CHECK (subtotal_amount >= 0),
    tax_amount NUMERIC(14,2) NOT NULL DEFAULT 0 CHECK (tax_amount >= 0),
    total_amount NUMERIC(14,2) NOT NULL CHECK (total_amount >= 0),
    outstanding_amount NUMERIC(14,2) NOT NULL CHECK (outstanding_amount >= 0),
    status TEXT NOT NULL CHECK (status IN ('draft', 'sent', 'partially_paid', 'paid', 'void', 'written_off')),
    payment_terms_days INTEGER CHECK (payment_terms_days >= 0),
    issued_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (due_date >= invoice_date),
    CHECK (outstanding_amount <= total_amount)
);

CREATE INDEX idx_invoice_customer_id ON invoice(customer_id);
CREATE INDEX idx_invoice_due_date ON invoice(due_date);
CREATE INDEX idx_invoice_status ON invoice(status);

CREATE TABLE payment (
    id UUID PRIMARY KEY,
    external_payment_id TEXT UNIQUE,
    invoice_id UUID NOT NULL REFERENCES invoice(id),
    customer_id UUID NOT NULL REFERENCES customer(id),
    payment_date DATE NOT NULL,
    amount NUMERIC(14,2) NOT NULL CHECK (amount > 0),
    currency CHAR(3) NOT NULL,
    payment_method TEXT,
    reference TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_payment_invoice_id ON payment(invoice_id);
CREATE INDEX idx_payment_customer_id ON payment(customer_id);
CREATE INDEX idx_payment_date ON payment(payment_date);

CREATE TABLE daily_cash_snapshot (
    id UUID PRIMARY KEY,
    snapshot_date DATE NOT NULL,
    currency CHAR(3) NOT NULL,
    opening_balance NUMERIC(14,2) NOT NULL,
    cash_in NUMERIC(14,2) NOT NULL DEFAULT 0,
    cash_out NUMERIC(14,2) NOT NULL DEFAULT 0,
    closing_balance NUMERIC(14,2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (snapshot_date, currency),
    CHECK (closing_balance = opening_balance + cash_in - cash_out)
);

CREATE TABLE risk_score (
    id UUID PRIMARY KEY,
    invoice_id UUID NOT NULL REFERENCES invoice(id),
    customer_id UUID NOT NULL REFERENCES customer(id),
    model_version TEXT NOT NULL,
    scored_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    late_payment_probability NUMERIC(5,4) NOT NULL CHECK (late_payment_probability >= 0 AND late_payment_probability <= 1),
    default_probability NUMERIC(5,4) CHECK (default_probability >= 0 AND default_probability <= 1),
    expected_days_late NUMERIC(8,2),
    predicted_payment_date DATE,
    risk_bucket TEXT NOT NULL CHECK (risk_bucket IN ('low', 'medium', 'high', 'critical')),
    top_reason_codes JSONB NOT NULL DEFAULT '[]'::jsonb
);

CREATE INDEX idx_risk_score_invoice_id ON risk_score(invoice_id);
CREATE INDEX idx_risk_score_customer_id ON risk_score(customer_id);
CREATE INDEX idx_risk_score_scored_at ON risk_score(scored_at DESC);

CREATE TABLE collection_recommendation (
    id UUID PRIMARY KEY,
    invoice_id UUID NOT NULL REFERENCES invoice(id),
    customer_id UUID NOT NULL REFERENCES customer(id),
    recommended_action TEXT NOT NULL,
    priority_rank INTEGER NOT NULL CHECK (priority_rank > 0),
    estimated_cash_impact NUMERIC(14,2),
    rationale TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_collection_recommendation_priority_rank ON collection_recommendation(priority_rank);
CREATE INDEX idx_collection_recommendation_invoice_id ON collection_recommendation(invoice_id);

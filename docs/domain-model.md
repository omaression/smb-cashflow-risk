# Domain Model

## Product goal
Help SMB finance teams predict short-term cash pressure and prioritize receivables follow-up before liquidity risk becomes operationally painful.

## Core modeling decisions
- The system is **customer-centric** for receivables risk.
- `invoice` is the primary prediction unit for late-payment risk.
- `daily_cash_snapshot` is the primary unit for cash-position forecasting.
- Recommendations are generated from invoice risk + customer exposure + expected cash impact.

## Entities

### customer
Represents the payer.

Key fields:
- `id`
- `external_customer_id`
- `name`
- `industry`
- `segment`
- `country`
- `payment_terms_days`
- `credit_limit`
- `is_active`

Derived metrics:
- average payment delay
- late payment ratio
- open exposure
- concentration share

### invoice
Represents a billed receivable.

Key fields:
- `id`
- `external_invoice_id`
- `customer_id`
- `invoice_date`
- `due_date`
- `currency`
- `subtotal_amount`
- `tax_amount`
- `total_amount`
- `outstanding_amount`
- `status`
- `payment_terms_days`

Statuses:
- `draft`
- `sent`
- `partially_paid`
- `paid`
- `void`
- `written_off`

Derived metrics:
- invoice age
- days until due
- days overdue
- collection priority

### payment
Represents a payment event, including partial payments.

Key fields:
- `id`
- `external_payment_id`
- `invoice_id`
- `customer_id`
- `payment_date`
- `amount`
- `currency`
- `payment_method`
- `reference`

### daily_cash_snapshot
Represents daily liquidity state.

Key fields:
- `id`
- `snapshot_date`
- `currency`
- `opening_balance`
- `cash_in`
- `cash_out`
- `closing_balance`

### risk_score
Stores model output for an open invoice.

Key fields:
- `id`
- `invoice_id`
- `customer_id`
- `model_version`
- `scored_at`
- `late_payment_probability`
- `default_probability`
- `expected_days_late`
- `predicted_payment_date`
- `risk_bucket`
- `top_reason_codes`

### collection_recommendation
Action the team should take.

Key fields:
- `id`
- `invoice_id`
- `customer_id`
- `recommended_action`
- `priority_rank`
- `estimated_cash_impact`
- `rationale`
- `created_at`

## Relationships
- one `customer` to many `invoice`
- one `invoice` to many `payment`
- one `invoice` to many historical `risk_score`
- one `invoice` to many `collection_recommendation` revisions

## Label definitions

### Late payment label
Binary target for first MVP risk model:
- `is_late_15` = 1 if invoice was paid more than 15 days after due date
- else 0

Why this target:
- practical for SMB collections
- easier to explain than a vague "bad debt risk" label
- realistic to compute from historical data

### Default / severe delinquency label
Optional second-stage target:
- `is_severely_delinquent` = 1 if invoice remains unpaid 60+ days after due date or is written off

## First-pass feature groups
- invoice size and terms
- invoice age and overdue state
- customer historical lateness
- customer payment consistency
- exposure concentration
- recent payment velocity
- seasonality / month / quarter effects

## Business priority formula
A first-pass collection priority score should combine:
- late-payment probability
- outstanding amount
- expected delay severity
- customer concentration risk

High probability on a tiny invoice should not outrank moderate probability on a strategically large exposure.

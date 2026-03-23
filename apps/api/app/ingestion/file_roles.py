"""
Comprehensive file role detection with header matching, content patterns, and fuzzy matching.

Supports real-world AR exports from QuickBooks, NetSuite, SAP, Oracle, IBM, and other ERP systems.

ATTRIBUTION:
- Content pattern detection approach inspired by csv-detective (github.com/datagouv/csv-detective)
- Levenshtein distance algorithm is a standard dynamic programming implementation
- AR aging column names compiled from QuickBooks, NetSuite, SAP, Oracle, IBM ERP documentation
- No code was copied from external sources; this implementation is original but methodology-informed

Research sources:
- csv-detective: Uses regex + content analysis for ~95% column type detection accuracy
- US Chamber: Standard AR aging report format (Customer, 0-30, 31-60, 61-90, Over 90)
- NetSuite/SAP/Oracle documentation: Column name variations for exports
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from io import StringIO
from typing import Any


@dataclass(frozen=True)
class FileRoleDetection:
    role: str | None
    confidence: float
    alternatives: list[tuple[str, float]]
    reasons: list[str]
    headers: list[str]
    row_count: int
    content_hints: dict[str, Any] = field(default_factory=dict)


# Comprehensive header aliases for each role
# Format: canonical_field -> list of variations found in real ERP/accounting exports
_ROLE_ALIASES: dict[str, tuple[str, ...]] = {
    "invoices": (
        # Standard invoice fields
        "invoice", "invoice_id", "invoice_number", "invoice_no", "inv", "inv_no",
        "invoice_num", "doc_number", "document_number", "doc_num", "tran_id",
        # Customer references
        "customer_id", "customer", "customer_name", "client", "client_id", "client_name",
        "account_id", "account_name", "account_number", "debtor",
        # Dates
        "invoice_date", "inv_date", "date", "document_date", "doc_date", "tran_date",
        "due_date", "due_dt", "due",
        # Amounts
        "total", "total_amount", "amount", "invoice_amount", "gross_amount", "net_amount",
        "subtotal", "subtotal_amount", "tax", "tax_amount",
        "balance", "outstanding", "outstanding_amount", "balance_due", "amount_due",
        "open_amount", "remaining", "remaining_amount",
        # Status and terms
        "status", "invoice_status", "terms", "payment_terms", "terms_name",
        "currency", "ccy",
    ),
    "payments": (
        # Payment identifiers
        "payment", "payment_id", "payment_no", "payment_number", "pay_id",
        "receipt", "receipt_no", "receipt_number", "remittance", "remittance_no",
        "reference", "reference_no", "ref", "ref_no",
        # Invoice references
        "invoice", "invoice_id", "invoice_no", "invoice_number",
        # Customer references
        "customer", "customer_id", "customer_name", "client", "client_id",
        # Dates
        "payment_date", "paid_date", "deposit_date", "date", "date_paid",
        # Amounts
        "amount", "amount_paid", "payment_amount", "paid_amount", "applied",
        "amount_applied", "paid",
        # Method info
        "method", "payment_method", "payment_type", "check_no", "check_number",
        "cheque_no", "cheque_number",
    ),
    "customers": (
        # Customer identifiers
        "customer", "customer_id", "customer_no", "customer_number", "customer_code",
        "account", "account_id", "account_no", "account_number", "account_code",
        "account_name", "client", "client_id", "client_no", "client_code",
        "debtor", "debtor_no", "debtor_id",
        # Names
        "name", "customer_name", "client_name", "company_name", "business_name",
        "legal_name", "trading_name", "company",
        # Address
        "address", "address1", "address2", "street", "city", "state", "province",
        "zip", "postal_code", "postcode", "country",
        # Contact
        "phone", "telephone", "email", "email_address", "contact", "contact_name",
        # Business info
        "industry", "segment", "segment_name", "category", "business_type",
        "terms", "payment_terms", "credit_limit", "credit_rating",
    ),
    "cash_snapshots": (
        # Date
        "date", "snapshot_date", "as_of", "as_of_date", "posting_date",
        # Balance columns
        "balance", "balance_date", "opening_balance", "opening", "start_balance",
        "closing_balance", "closing", "end_balance", "bank_balance",
        "cash_balance", "cash",
        # Flows
        "cash_in", "inflow", "inflows", "receipts", "deposits",
        "cash_out", "outflow", "outflows", "payments", "withdrawals",
        # Currency
        "currency", "ccy", "account_currency",
    ),
    "unpaid_invoice_export": (
        # === MOST IMPORTANT: This is the most common BYOD format ===
        # Invoice identifiers (all variations)
        "invoice", "invoice_id", "invoice_no", "invoice_number", "inv", "inv_no",
        "invoice_num", "doc_num", "doc_number", "document_number", "tran_id",
        # Customer/account (all variations)
        "customer", "customer_id", "customer_no", "customer_number",
        "customer_name", "client", "client_id", "client_name",
        "account", "account_id", "account_no", "account_number", "account_name",
        "debtor", "debtor_no", "debtor_id", "debtor_name",
        "business", "company", "company_name",
        # Dates
        "date", "invoice_date", "inv_date", "document_date", "doc_date", "tran_date",
        "due", "due_date", "due_dt",
        "as_of", "as_of_date", "report_date", "snapshot_date",
        # Amounts (all variations)
        "amount", "total", "total_amount", "invoice_amount", "gross",
        "balance", "outstanding", "outstanding_amount", "balance_due",
        "open_amount", "remaining", "remaining_amount", "amount_due",
        "original", "original_amount", "billed",
        # Status
        "status", "invoice_status", "doc_status", "tran_status",
        "paid", "paid_flag", "is_paid", "open", "closed",
        "terms", "payment_terms", "terms_name", "terms_code",
        "currency", "ccy",
        # Aging buckets (standard variations)
        "current", "cur", "0_30", "0_to_30", "1_30", "1_to_30", "under_30",
        "30", "30_days", "thirty_days",
        "31_60", "31_to_60", "31_60_days", "thirty_sixty",
        "60", "60_days", "sixty_days",
        "61_90", "61_to_90", "61_90_days", "sixty_ninety",
        "90", "90_days", "ninety_days",
        "over_90", "90_plus", "over_ninety", "gt_90",
        "91_120", "120_days", "120_plus",
        "aging_1", "aging_2", "aging_3", "aging_4", "aging_5",
        "bucket_1", "bucket_2", "bucket_3", "bucket_4", "bucket_5",
        # IBM-specific
        "ar", "receivable", "receivables", "account_receivable",
        "credit", "debit", "credit_amt", "debit_amt",
    ),
}

# Filename hints for each role
_FILENAME_HINTS: dict[str, tuple[str, ...]] = {
    "invoices": ("invoice", "inv_", "ar_", "receivable"),
    "payments": ("payment", "receipt", "cashapp", "remittance", "paid"),
    "customers": ("customer", "client", "account", "debtor"),
    "cash_snapshots": ("cash", "snapshot", "balance", "bank", "treasury"),
    "unpaid_invoice_export": (
        "unpaid", "open_invoice", "outstanding", "aging", "ar", "receivable",
        "trial_balance", "accounts", "ar_aging", "receivables", "debtor",
        "ibm", "oracle", "sap_", "netsuite", "qb_", "quickbook",
        "export", "report", "aging_report", "ar_report", "ar_export",
    ),
}

# Content patterns to detect in actual data values
_CONTENT_PATTERNS: dict[str, dict[str, re.Pattern]] = {
    "unpaid_invoice_export": {
        "invoice_pattern": re.compile(r"^(inv[-_]?\d+|#\d{4,}|i[-_]?\d{4,}|\d{4,})$", re.IGNORECASE),
        "currency_pattern": re.compile(r"^\$?\s*-?\d{1,3}(,\d{3})*(\.\d{2})?$"),
        "date_pattern": re.compile(r"^\d{4}[-/]\d{2}[-/]\d{2}$|^\d{2}[-/]\d{2}[-/]\d{4}$"),
        "aging_bucket": re.compile(r"^(current|0[-_]?30|31[-_]?60|61[-_]?90|90[-_]?plus|over[-_]?90)$", re.IGNORECASE),
    },
    "invoices": {
        "invoice_pattern": re.compile(r"^(inv[-_]?\d+|#\d{4,}|i[-_]?\d{4,}|\d{4,})$", re.IGNORECASE),
        "currency_pattern": re.compile(r"^\$?\s*-?\d{1,3}(,\d{3})*(\.\d{2})?$"),
        "date_pattern": re.compile(r"^\d{4}[-/]\d{2}[-/]\d{2}$|^\d{2}[-/]\d{2}[-/]\d{4}$"),
    },
    "payments": {
        "payment_pattern": re.compile(r"^(pay[-_]?\d+|p[-_]?\d{4,}|receipt[-_]?\d+)$", re.IGNORECASE),
        "currency_pattern": re.compile(r"^\$?\s*-?\d{1,3}(,\d{3})*(\.\d{2})?$"),
        "date_pattern": re.compile(r"^\d{4}[-/]\d{2}[-/]\d{2}$|^\d{2}[-/]\d{2}[-/]\d{4}$"),
    },
    "customers": {
        "customer_id_pattern": re.compile(r"^(cust[-_]?\d+|c[-_]?\d{4,}|\d{4,})$", re.IGNORECASE),
    },
}


def _normalize_token(value: str) -> str:
    """Normalize a header or field name for matching."""
    value = value.strip().lower()
    # Replace common separators with underscore
    value = re.sub(r"[\s\-\.]+", "_", value)
    # Remove non-alphanumeric except underscore
    value = re.sub(r"[^a-z0-9_]", "", value)
    # Collapse multiple underscores
    value = re.sub(r"_+", "_", value).strip("_")
    return value


def _fuzzy_match(header: str, aliases: tuple[str, ...], max_distance: int = 2) -> tuple[bool, str | None]:
    """
    Check if header fuzzy-matches any alias within max_distance edits.
    
    Returns (matched, matched_alias) tuple.
    """
    normalized = _normalize_token(header)
    for alias in aliases:
        alias_norm = _normalize_token(alias)
        # Exact match
        if normalized == alias_norm:
            return True, alias
        # Prefix match (handles abbreviations)
        if normalized.startswith(alias_norm) or alias_norm.startswith(normalized):
            if len(normalized) >= 3 and len(alias_norm) >= 3:
                return True, alias
        # Levenshtein distance for typos
        if len(normalized) >= 4 and len(alias_norm) >= 4:
            distance = _levenshtein_distance(normalized, alias_norm)
            if distance <= max_distance:
                return True, alias
    return False, None


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def _read_headers_and_count(contents: bytes) -> tuple[list[str], int]:
    """Read CSV headers and row count."""
    text = contents.decode("utf-8-sig", errors="replace")
    reader = csv.reader(StringIO(text))
    rows = list(reader)
    if not rows:
        return [], 0
    headers = [_normalize_token(cell) for cell in rows[0]]
    row_count = max(0, len(rows) - 1)
    return headers, row_count


def _sample_content(contents: bytes, sample_size: int = 100) -> list[dict[str, str]]:
    """Sample first N rows of content for pattern detection."""
    text = contents.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(StringIO(text))
    if not reader.fieldnames:
        return []
    return [row for row, _ in zip(reader, range(sample_size))]


def _detect_by_content_patterns(
    sample_rows: list[dict[str, str]],
    headers: list[str],
) -> dict[str, float]:
    """
    Detect file role based on content patterns.
    
    Returns a dict of role -> confidence score (0-1).
    """
    if not sample_rows or not headers:
        return {}
    
    scores: dict[str, float] = {}
    header_set = set(headers)
    normalized_to_original = {h: h for h in headers}
    
    for role, patterns in _CONTENT_PATTERNS.items():
        score = 0.0
        matches = 0
        
        # Check each pattern against sample data
        for header in headers:
            col_values = []
            for row in sample_rows:
                val = row.get(header, row.get(header, ""))
                if val:
                    col_values.append(val)
            
            if not col_values:
                continue
            
            # Check if column matches expected patterns for this role
            for pattern_name, pattern in patterns.items():
                match_count = sum(1 for v in col_values if pattern.match(str(v)))
                match_ratio = match_count / len(col_values) if col_values else 0
                
                if match_ratio > 0.5:  # More than 50% of values match
                    score += 0.15
                    matches += 1
        
        # Bonus for header + content alignment
        if role == "unpaid_invoice_export":
            # Check for aging buckets in headers
            aging_headers = {"current", "0_30", "31_60", "61_90", "over_90", 
                           "aging_1", "aging_2", "aging_3", "aging_4",
                           "bucket_1", "bucket_2", "bucket_3", "bucket_4"}
            aging_matches = aging_headers & header_set
            if len(aging_matches) >= 2:
                score += 0.25
            
            # Check for customer + amount + date combination
            has_customer = bool(header_set & {"customer", "customer_name", "account", "account_name", "debtor"})
            has_amount = bool(header_set & {"amount", "balance", "outstanding", "total", "original"})
            has_date = bool(header_set & {"date", "invoice_date", "due_date", "as_of"})
            
            if has_customer and has_amount and has_date:
                score += 0.15
        
        scores[role] = min(score, 0.95)
    
    return scores


def detect_file_role(*, filename: str, contents: bytes) -> FileRoleDetection:
    """
    Detect the role of a CSV file based on filename, headers, and content patterns.
    
    Uses a hybrid approach:
    1. Header alias matching (40% weight)
    2. Content pattern detection (40% weight)
    3. Filename hints (20% weight)
    """
    headers, row_count = _read_headers_and_count(contents)
    header_set = set(headers)
    filename_norm = _normalize_token(filename)
    
    # Sample content for pattern detection
    sample_rows = _sample_content(contents, sample_size=100)
    content_scores = _detect_by_content_patterns(sample_rows, headers)
    
    # Calculate scores from each detection method
    header_scores: dict[str, float] = {}
    header_reasons: dict[str, list[str]] = {}
    
    for role, aliases in _ROLE_ALIASES.items():
        score = 0.0
        reasons: list[str] = []
        
        # Header matching with fuzzy matching
        alias_hits = []
        for alias in aliases:
            alias_norm = _normalize_token(alias)
            if alias_norm in header_set:
                alias_hits.append(alias)
            else:
                # Try fuzzy matching for each header
                for header in headers:
                    matched, matched_alias = _fuzzy_match(header, (alias,), max_distance=1)
                    if matched:
                        alias_hits.append(f"{alias}~{header}")
                        break
        
        if alias_hits:
            # Weight by number of matches, with diminishing returns
            score += min(0.70, 0.10 * len(alias_hits) + 0.05 * min(len(alias_hits), 5))
            reasons.append(f"matched headers: {', '.join(str(h).split('~')[0] for h in alias_hits[:7])}")
        
        # Filename hints
        filename_hits = [hint for hint in _FILENAME_HINTS.get(role, ()) if hint in filename_norm]
        if filename_hits:
            score += min(0.15, 0.05 * len(filename_hits))
            reasons.append(f"filename hints: {', '.join(filename_hits)}")
        
        header_scores[role] = min(score, 0.99)
        header_reasons[role] = reasons
    
    # Combine header and content scores
    combined_scores: dict[str, float] = {}
    all_reasons: dict[str, list[str]] = {}
    
    for role in _ROLE_ALIASES:
        header_score = header_scores.get(role, 0.0)
        content_score = content_scores.get(role, 0.0)
        
        # Weighted combination: 40% header, 40% content, 20% filename
        # But if content detection found patterns, give it more weight
        if content_score > 0.3:
            combined = header_score * 0.35 + content_score * 0.45 + header_score * 0.20
        else:
            combined = header_score * 0.60 + content_score * 0.40
        
        combined_scores[role] = min(combined, 0.99)
        all_reasons[role] = header_reasons.get(role, [])
        
        # Add content detection reasons
        if content_score > 0.15:
            all_reasons[role].append(f"content patterns detected (confidence: {int(content_score * 100)}%)")
    
    # Find top role
    ranked = sorted(combined_scores.items(), key=lambda item: item[1], reverse=True)
    top_role, top_score = ranked[0] if ranked else (None, 0.0)
    
    # Collect all reasons for the top role
    final_reasons = all_reasons.get(top_role, [])
    
    # Preference logic: unpaid_invoice_export over invoices for AR patterns
    # If we have customer + amount + due_date but not full invoice details, prefer unpaid_invoice_export
    if top_role == "invoices" and "unpaid_invoice_export" in combined_scores:
        uie_score = combined_scores.get("unpaid_invoice_export", 0)
        if uie_score >= top_score * 0.8:  # Close score
            # Check if we have the typical AR aging pattern
            has_customer = bool(header_set & {"customer", "customer_name", "account", "account_name", "debtor"})
            has_amount = bool(header_set & {"amount", "balance", "outstanding", "total", "original"})
            has_due_date = bool(header_set & {"due_date", "due", "date"})
            has_invoice_details = bool(header_set & {"invoice_id", "invoice_no", "invoice_number"} & header_set)
            
            # If we have customer + amount + due_date but lack full invoice details, this is an AR export
            if has_customer and has_amount and has_due_date and not has_invoice_details:
                top_role = "unpaid_invoice_export"
                top_score = max(top_score, uie_score)
                final_reasons = all_reasons.get(top_role, [])
                if "appears to be an AR aging export" not in final_reasons:
                    final_reasons.append("appears to be an AR aging export")
    
    # Check for ambiguous case: top score is low and scores are uniformly distributed
    if len(ranked) >= 2:
        second_score = ranked[1][1] if len(ranked) > 1 else 0
        # If top and second scores are very close and both low, it's ambiguous
        if top_score < 0.25 and abs(top_score - second_score) < 0.1:
            return FileRoleDetection(
                role=None,
                confidence=0.0,
                alternatives=ranked[:3],
                reasons=["headers and content are too ambiguous to determine file role"],
                headers=headers,
                row_count=row_count,
                content_hints={"sample_size": len(sample_rows)},
            )
    
    # Lower threshold to be more permissive
    if top_score < 0.10:
        return FileRoleDetection(
            role=None,
            confidence=0.0,
            alternatives=ranked[:3],
            reasons=["not enough recognizable headers or content patterns to infer a reliable file role"],
            headers=headers,
            row_count=row_count,
            content_hints={"sample_size": len(sample_rows)},
        )
    
    # Add content hints to result
    content_hints = {
        "sample_size": len(sample_rows),
        "header_count": len(headers),
        "has_aging_buckets": bool({"current", "0_30", "31_60", "61_90", "over_90"} & header_set),
        "has_customer": bool({"customer", "customer_name", "account", "debtor"} & header_set),
        "has_amount": bool({"amount", "balance", "outstanding", "total"} & header_set),
        "has_date": bool({"date", "invoice_date", "due_date", "as_of"} & header_set),
    }
    
    return FileRoleDetection(
        role=top_role,
        confidence=round(top_score, 2),
        alternatives=[(role, round(score, 2)) for role, score in ranked[1:4]],
        reasons=final_reasons if final_reasons else ["matched by combined analysis"],
        headers=headers,
        row_count=row_count,
        content_hints=content_hints,
    )
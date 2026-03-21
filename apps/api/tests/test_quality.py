from app.ingestion.quality import (
    QualityDimension,
    QualityProfile,
    build_quality_profile,
    compute_completeness,
    compute_consistency,
    compute_coverage,
    compute_history_depth,
    compute_sample_size,
    generate_recommendations,
    reliability_grade,
)


def test_compute_completeness_ideal_case() -> None:
    result = compute_completeness(
        required_fields=["invoice_id", "customer_id", "due_date"],
        present_fields=["invoice_id", "customer_id", "due_date"],
        row_count=100,
        missing_field_ratio=0.0,
    )
    assert result.score >= 0.9
    assert len(result.issues) == 0


def test_compute_completeness_missing_required_fields() -> None:
    result = compute_completeness(
        required_fields=["invoice_id", "customer_id", "due_date"],
        present_fields=["invoice_id"],
        row_count=100,
        missing_field_ratio=0.6,
    )
    assert result.score < 0.7
    assert any("Missing required fields" in issue for issue in result.issues)


def test_compute_completeness_empty_dataset() -> None:
    result = compute_completeness(
        required_fields=["invoice_id"],
        present_fields=[],
        row_count=0,
        missing_field_ratio=1.0,
    )
    assert result.score == 0.0
    assert "Empty dataset" in result.issues


def test_compute_consistency_no_violations() -> None:
    result = compute_consistency(
        duplicate_id_count=0,
        ambiguous_mapping_count=0,
        temporal_violation_count=0,
        amount_violation_count=0,
        status_violation_count=0,
        row_count=100,
    )
    assert result.score >= 0.9
    assert len(result.issues) == 0


def test_compute_consistency_duplicate_ids() -> None:
    result = compute_consistency(
        duplicate_id_count=5,
        ambiguous_mapping_count=0,
        temporal_violation_count=0,
        amount_violation_count=0,
        status_violation_count=0,
        row_count=100,
    )
    assert result.score < 1.0
    assert any("duplicate IDs" in issue for issue in result.issues)


def test_compute_consistency_temporal_violations() -> None:
    result = compute_consistency(
        duplicate_id_count=0,
        ambiguous_mapping_count=0,
        temporal_violation_count=10,
        amount_violation_count=0,
        status_violation_count=0,
        row_count=100,
    )
    assert result.score < 0.9
    assert any("temporal inconsistencies" in issue for issue in result.issues)


def test_compute_consistency_status_violations() -> None:
    result = compute_consistency(
        duplicate_id_count=0,
        ambiguous_mapping_count=0,
        temporal_violation_count=0,
        amount_violation_count=0,
        status_violation_count=7,
        row_count=50,
    )
    assert result.score < 1.0
    assert any("status inconsistencies" in issue for issue in result.issues)


def test_compute_consistency_empty_dataset() -> None:
    result = compute_consistency(
        duplicate_id_count=0,
        ambiguous_mapping_count=0,
        temporal_violation_count=0,
        amount_violation_count=0,
        status_violation_count=0,
        row_count=0,
    )
    assert result.score == 0.0
    assert "Empty dataset" in result.issues


def test_compute_coverage_with_payments() -> None:
    result = compute_coverage(
        observed_customers=10,
        observed_invoices=100,
        observed_payments=50,
        expected_customer_count=None,
        expected_invoice_count=None,
    )
    assert result.score >= 0.7
    assert len(result.issues) == 0


def test_compute_coverage_no_payments() -> None:
    result = compute_coverage(
        observed_customers=10,
        observed_invoices=100,
        observed_payments=0,
        expected_customer_count=None,
        expected_invoice_count=None,
    )
    assert "No payment history available" in result.issues


def test_compute_coverage_no_customers() -> None:
    result = compute_coverage(
        observed_customers=0,
        observed_invoices=10,
        observed_payments=0,
        expected_customer_count=None,
        expected_invoice_count=None,
    )
    assert result.score < 0.5
    assert "No customers observed" in result.issues


def test_compute_history_depth_healthy() -> None:
    result = compute_history_depth(
        earliest_date_days_ago=90,
        latest_date_days_ago=0,
        payment_history_months=12,
    )
    assert result.score >= 0.4
    assert len(result.issues) == 0


def test_compute_history_depth_stale_start() -> None:
    result = compute_history_depth(
        earliest_date_days_ago=400,
        latest_date_days_ago=300,
        payment_history_months=0,
    )
    assert result.score < 1.0
    assert any("days ago" in issue for issue in result.issues)


def test_compute_history_depth_no_temporal_data() -> None:
    result = compute_history_depth(
        earliest_date_days_ago=None,
        latest_date_days_ago=None,
        payment_history_months=None,
    )
    assert result.score == 0.0
    assert "No temporal data available" in result.issues


def test_compute_sample_size_adequate() -> None:
    result = compute_sample_size(invoice_count=200, customer_count=20)
    assert result.score >= 0.8
    assert len(result.issues) == 0


def test_compute_sample_size_too_few_invoices() -> None:
    result = compute_sample_size(invoice_count=30, customer_count=5)
    assert result.score < 1.0
    assert any("invoices" in issue for issue in result.issues)


def test_compute_sample_size_too_few_customers() -> None:
    result = compute_sample_size(invoice_count=100, customer_count=2)
    assert any("customers" in issue for issue in result.issues)


def test_reliability_grade_boundaries() -> None:
    assert reliability_grade(0.90) == "high"
    assert reliability_grade(0.85) == "high"
    assert reliability_grade(0.84) == "moderate"
    assert reliability_grade(0.65) == "moderate"
    assert reliability_grade(0.64) == "low"
    assert reliability_grade(0.40) == "low"
    assert reliability_grade(0.39) == "insufficient"
    assert reliability_grade(0.0) == "insufficient"


def test_generate_recommendations_includes_payment_advice() -> None:
    recs = generate_recommendations(
        completeness=QualityDimension(name="completeness", score=0.9, weight=0.25),
        consistency=QualityDimension(name="consistency", score=0.9, weight=0.20),
        coverage=QualityDimension(name="coverage", score=0.9, weight=0.20),
        history_depth=QualityDimension(name="history_depth", score=0.9, weight=0.20),
        sample_size=QualityDimension(name="sample_size", score=0.9, weight=0.15),
        observed_payments=0,
    )
    assert any("payment history" in rec.lower() for rec in recs)


def test_build_quality_profile_ideal_case() -> None:
    profile = build_quality_profile(
        required_fields=["invoice_id", "customer_id", "due_date"],
        present_fields=["invoice_id", "customer_id", "due_date"],
        row_count=200,
        missing_field_ratio=0.0,
        duplicate_id_count=0,
        ambiguous_mapping_count=0,
        temporal_violation_count=0,
        amount_violation_count=0,
        status_violation_count=0,
        observed_customers=20,
        observed_invoices=200,
        observed_payments=150,
        expected_customer_count=None,
        expected_invoice_count=None,
        earliest_date_days_ago=365,
        latest_date_days_ago=0,
        payment_history_months=12,
    )
    assert profile.overall_score >= 0.65
    assert profile.reliability_grade in {"high", "moderate"}
    assert len(profile.recommendations) <= 5


def test_build_quality_profile_poor_case() -> None:
    profile = build_quality_profile(
        required_fields=["invoice_id", "customer_id", "due_date"],
        present_fields=["invoice_id"],
        row_count=10,
        missing_field_ratio=0.6,
        duplicate_id_count=3,
        ambiguous_mapping_count=2,
        temporal_violation_count=5,
        amount_violation_count=1,
        status_violation_count=4,
        observed_customers=1,
        observed_invoices=10,
        observed_payments=0,
        expected_customer_count=None,
        expected_invoice_count=None,
        earliest_date_days_ago=30,
        latest_date_days_ago=0,
        payment_history_months=None,
    )
    assert profile.overall_score < 0.5
    assert profile.reliability_grade in {"low", "insufficient"}
    assert len(profile.recommendations) >= 1


def test_build_quality_profile_handles_zero_row_count() -> None:
    profile = build_quality_profile(
        required_fields=["invoice_id"],
        present_fields=[],
        row_count=0,
        missing_field_ratio=1.0,
        duplicate_id_count=0,
        ambiguous_mapping_count=0,
        temporal_violation_count=0,
        amount_violation_count=0,
        status_violation_count=0,
        observed_customers=0,
        observed_invoices=0,
        observed_payments=0,
    )
    assert profile.overall_score == 0.0
    assert profile.reliability_grade == "insufficient"
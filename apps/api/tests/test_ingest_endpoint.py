from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "raw"


def test_import_csv_endpoint(client) -> None:
    response = client.post(
        "/api/v1/import/csv",
        data={"entity_type": "customers"},
        files={"file": ("sample_customers.csv", (DATA_DIR / "sample_customers.csv").read_bytes(), "text/csv")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["entity_type"] == "customers"
    assert payload["imported"] == 3
    assert payload["rejected"] == 0

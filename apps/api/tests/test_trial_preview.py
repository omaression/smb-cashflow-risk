def test_trial_preview_endpoint_returns_workspace_summary(client) -> None:
    response = client.post(
        "/api/v1/trial/preview",
        files=[("files", ("ugly-ar-export.csv", b"invoice,customer,amount\nINV-1,Acme,100\n", "text/csv"))],
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "preview_ready"
    assert payload["source_file_count"] == 1
    assert payload["files"][0]["filename"] == "ugly-ar-export.csv"
    assert payload["quality_profile"]["reliability_grade"] == "low"
    assert payload["quality_profile"]["recommendations"]


def test_trial_status_endpoint_returns_preview_workspace(client) -> None:
    preview = client.post(
        "/api/v1/trial/preview",
        files=[("files", ("ugly-ar-export.csv", b"invoice,customer,amount\nINV-1,Acme,100\n", "text/csv"))],
    )
    workspace_id = preview.json()["workspace_id"]

    response = client.get(f"/api/v1/trial/{workspace_id}/status")
    assert response.status_code == 200
    payload = response.json()

    assert payload["workspace_id"] == workspace_id
    assert payload["status"] == "preview_ready"
    assert payload["quality_profile"]["issue_summary"]["high"] == 1

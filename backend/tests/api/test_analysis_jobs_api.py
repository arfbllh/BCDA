def test_create_analysis_job_validation_error(client):
    response = client.post("/api/v1/analysis/jobs", json={"job_type": "survival"})
    assert response.status_code == 400
    payload = response.get_json()
    assert "error" in payload
    assert payload["error"]["code"] == "VALIDATION_ERROR"


def test_create_analysis_job_and_poll_status_and_result(client):
    create_response = client.post(
        "/api/v1/analysis/jobs",
        json={
            "study_id": "brca_tcga_pub2015",
            "job_type": "survival",
            "parameters": {"gene": "TP53"},
        },
    )
    assert create_response.status_code == 202
    created = create_response.get_json()
    assert created["job_id"].startswith("job_")

    job_id = created["job_id"]
    status_response = client.get(f"/api/v1/analysis/jobs/{job_id}")
    assert status_response.status_code == 200
    status_payload = status_response.get_json()
    assert status_payload["job_id"] == job_id
    assert status_payload["status"] in {"queued", "running", "completed", "failed"}

    result_response = client.get(f"/api/v1/analysis/jobs/{job_id}/result")
    assert result_response.status_code == 200
    result_payload = result_response.get_json()
    assert result_payload["job_id"] == job_id
    assert "result" in result_payload
    assert result_payload["result"]["job_type"] == "survival"


def test_llm_infer_job_stub_when_not_configured(client):
    create_response = client.post(
        "/api/v1/analysis/jobs",
        json={
            "study_id": "brca_tcga_pub2015",
            "job_type": "llm_infer",
            "parameters": {"prompt": "What cohort is this?"},
        },
    )
    assert create_response.status_code == 202
    job_id = create_response.get_json()["job_id"]

    result_response = client.get(f"/api/v1/analysis/jobs/{job_id}/result")
    assert result_response.status_code == 200
    body = result_response.get_json()
    assert body["result"]["job_type"] == "llm_infer"
    assert body["result"]["llm_mode"] == "stub"
    assert "assistant_message" in body["result"]


def test_job_not_found_returns_standard_error(client):
    response = client.get("/api/v1/analysis/jobs/job_missing_123")
    assert response.status_code == 404
    payload = response.get_json()
    assert payload["error"]["code"] == "JOB_NOT_FOUND"


def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    data = r.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "bcancerportal-backend"


def test_readyz_with_sqlite(client):
    r = client.get("/readyz")
    assert r.status_code == 200
    body = r.get_json()
    assert body["ready"] is True
    assert body["checks"]["db"] is True


def test_openapi_v1_json(client):
    r = client.get("/api/v1/openapi.json")
    assert r.status_code == 200
    spec = r.get_json()
    assert spec.get("openapi")
    assert "paths" in spec


def test_summary_rejects_invalid_study_id(client):
    r = client.get("/api/v1/datasets/../x/summary")
    assert r.status_code == 404

    r2 = client.get("/api/v1/datasets/9bad/summary")
    assert r2.status_code == 400
    assert "error" in r2.get_json()


def test_legacy_openapi_path(client):
    r = client.get("/api/openapi.json")
    assert r.status_code == 200
    assert r.get_json().get("openapi")


def test_study_data_status_invalid_study(client):
    r = client.get("/api/v1/datasets/9bad/data-status")
    assert r.status_code == 400
    body = r.get_json()
    assert body.get("error", {}).get("code") == "INVALID_REQUEST"


def test_study_data_status_ok_shape(client):
    r = client.get("/api/v1/datasets/brca_tcga_pub2015/data-status")
    assert r.status_code == 200
    body = r.get_json()
    assert body["study_id"] == "brca_tcga_pub2015"
    assert "clinical_patient_ingested" in body
    assert "clinical_sample_ingested" in body
    assert "mutations_table" in body
    assert "gistic_table" in body
    assert "summary_ready" in body
    assert body["summary_ready"] is False
    assert "expression_matrix_file_present" in body
    assert "expression_matrix_source_present" in body


def test_datasets_default_empty_without_clinical_table(client, app):
    from extensions import db
    from models.study import Study

    with app.app_context():
        db.session.add(
            Study(
                study_id="ghost_study",
                type_of_cancer="Breast",
                name="Ghost",
                is_active=True,
            )
        )
        db.session.commit()

    r = client.get("/api/v1/datasets")
    assert r.status_code == 200
    body = r.get_json()
    for rows in body.values():
        assert not any(d.get("id") == "ghost_study" for d in rows)

    r_full = client.get("/api/v1/datasets?full_catalog=1")
    assert r_full.status_code == 200
    full = r_full.get_json()
    breast = full.get("Breast", [])
    assert any(d.get("id") == "ghost_study" for d in breast)


def test_datasets_lists_study_after_clinical_table_exists(client, app):
    from sqlalchemy import text

    from extensions import db
    from models.study import Study

    with app.app_context():
        db.session.add(
            Study(
                study_id="ingested_demo",
                type_of_cancer="Breast",
                name="Ingested Demo",
                is_active=True,
            )
        )
        db.session.commit()
        db.session.execute(
            text(
                "CREATE TABLE ingested_demo_data_clinical_patient ("
                "patient_id VARCHAR(64), os_status VARCHAR(32), os_months FLOAT, "
                "age INT, race VARCHAR(64), sex VARCHAR(32), "
                "ajcc_pathologic_tumor_stage VARCHAR(64), days_to_birth VARCHAR(64), "
                "days_to_last_followup VARCHAR(64), dfs_months VARCHAR(64), dfs_status VARCHAR(64))"
            )
        )
        db.session.commit()

    r = client.get("/api/v1/datasets")
    assert r.status_code == 200
    body = r.get_json()
    breast = body.get("Breast", [])
    assert any(d.get("id") == "ingested_demo" for d in breast)


def test_summary_not_ingested_without_study_tables(client):
    r = client.get("/api/v1/datasets/brca_tcga_pub2015/summary")
    assert r.status_code == 404
    body = r.get_json()
    assert body.get("error", {}).get("code") == "NOT_INGESTED"
    assert "missing" in body.get("error", {}).get("message", "").lower()

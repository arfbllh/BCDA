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

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

SERVICE_ROOT = Path(__file__).resolve().parents[1]
if str(SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_ROOT))

from main import app
from src.api import routes
from src.core.storage import Database


VALID_CONFIG = {
    "config_version": "1.0",
    "global": {"env": "prod"},
    "extensions": {"password": "secret_value"},
}


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    test_db = Database(str(tmp_path / "config.db"))
    monkeypatch.setattr(routes, "DB", test_db)
    with TestClient(app) as test_client:
        yield test_client


def test_validate_and_normalize_redact_sensitive_values(client: TestClient) -> None:
    validate_response = client.post(
        "/api/config/validate",
        json={"config": VALID_CONFIG, "strict": True},
    )
    assert validate_response.status_code == 200
    assert validate_response.json()["valid"] is True
    assert validate_response.json()["normalized_config"]["extensions"]["password"] == "***"

    normalize_response = client.post("/api/config/normalize", json={"config": VALID_CONFIG})
    assert normalize_response.status_code == 200
    assert len(normalize_response.json()["config_digest"]) == 64
    assert normalize_response.json()["normalized_config"]["extensions"]["password"] == "***"


def test_draft_publish_history_and_export_flow(client: TestClient) -> None:
    headers = {
        "Idempotency-Key": "draft-key-1",
        "X-Talos-Principal-Id": "user-1",
    }
    create_response = client.post(
        "/api/config/drafts",
        json={"config": VALID_CONFIG, "note": "Initial version"},
        headers=headers,
    )
    assert create_response.status_code == 200
    create_body = create_response.json()
    draft_id = create_body["draft_id"]

    replay_response = client.post(
        "/api/config/drafts",
        json={"config": VALID_CONFIG, "note": "Initial version"},
        headers=headers,
    )
    assert replay_response.status_code == 200
    assert replay_response.json()["draft_id"] == draft_id

    publish_response = client.post(
        "/api/config/publish",
        json={"draft_id": draft_id},
        headers={
            "Idempotency-Key": "publish-key-1",
            "X-Talos-Principal-Id": "admin-1",
        },
    )
    assert publish_response.status_code == 200

    history_response = client.get("/api/config/history?limit=10")
    assert history_response.status_code == 200
    assert history_response.json()["items"][0]["redacted_config"]["extensions"]["password"] == "***"

    export_response = client.post("/api/config/export", json={"format": "yaml"})
    assert export_response.status_code == 200
    assert "***" in export_response.json()["content"]

    draft_export_response = client.post("/api/config/export", json={"format": "yaml", "source": "draft", "draft_id": draft_id})
    assert draft_export_response.status_code == 200
    assert "***" in draft_export_response.json()["content"]

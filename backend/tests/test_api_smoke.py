# Smoke tests for FastAPI routes that don't require live LLM/Nutrient calls
# (sepsis vitals / prescription submission are excluded here since they'd
# make real paid API calls on every test run — those were verified manually
# against the live backend instead; see project history).

from fastapi.testclient import TestClient

from main import app


def test_root_endpoint():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_list_patients_returns_three_simulated_patients():
    with TestClient(app) as client:
        response = client.get("/api/patients")
        assert response.status_code == 200
        patients = response.json()
        assert len(patients) == 3
        patient_ids = {p["patient_id"] for p in patients}
        assert patient_ids == {"P-001", "P-002", "P-003"}


def test_download_audit_404_for_unknown_patient():
    with TestClient(app) as client:
        response = client.get("/api/download-audit/NO-SUCH-PATIENT")
        assert response.status_code == 404


def test_download_report_404_for_unknown_patient():
    with TestClient(app) as client:
        response = client.get("/api/download-report/NO-SUCH-PATIENT")
        assert response.status_code == 404


def test_websocket_endpoints():
    with TestClient(app) as client:
        for endpoint in ("/ws", "/api/ws"):
            with client.websocket_connect(endpoint) as ws:
                ack = ws.receive_json()
                assert ack["type"] == "connection_established"
                ws.send_text("ping")
                reply = ws.receive_text()
                assert reply == "pong"


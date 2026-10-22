# I use these tests to make sure the dashboard receives a reliable response and
# that invalid experiment sizes are rejected before analysis begins.

from fastapi.testclient import TestClient

from equilibrium_lab.api import app

client = TestClient(app)


def test_health_and_brief_endpoints():
    assert client.get("/api/health").json() == {"status": "ok"}
    response = client.get("/api/brief?seed=29&zones=12")
    assert response.status_code == 200
    assert response.json()["experiment"]["zones"] == 12


def test_invalid_zone_count_is_rejected():
    assert client.get("/api/brief?zones=3").status_code == 422


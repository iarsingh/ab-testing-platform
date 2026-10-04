from fastapi.testclient import TestClient
from abtest.main import app

client = TestClient(app)


def test_clear_lift_picks_treatment():
    payload = client.post("/analyze", json={
        "control_success": 10, "control_n": 200,
        "treatment_success": 80, "treatment_n": 200,
    }).json()
    assert payload["winner"] == "treatment"
    assert payload["lift"] > 0


def test_bad_counts_are_refused():
    assert client.post("/analyze", json={
        "control_success": 5, "control_n": 3,
        "treatment_success": 1, "treatment_n": 10,
    }).status_code == 422

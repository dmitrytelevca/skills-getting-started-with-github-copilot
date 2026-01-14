from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_signup_updates_activities():
    activity = "Basketball Team"
    email = "pytest.refresh@example.com"

    # Ensure not already present
    resp = client.get("/activities")
    assert resp.status_code == 200
    activities = resp.json()
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Sign up
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert "Signed up" in resp.json()["message"]

    # Fetch activities and verify participant present
    resp = client.get("/activities")
    assert resp.status_code == 200
    activities = resp.json()
    assert email in activities[activity]["participants"]

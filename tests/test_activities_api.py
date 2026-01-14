from uuid import uuid4
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_remove_flow():
    activity = "Basketball Team"
    email = f"pytest.{uuid4().hex}@example.com"

    # Ensure clean state
    resp = client.get("/activities")
    assert resp.status_code == 200
    if email in resp.json()[activity]["participants"]:
        client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Sign up
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert "Signed up" in resp.json()["message"]

    # Ensure participant is present
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email in resp.json()[activity]["participants"]

    # Remove participant
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp.status_code == 200
    assert "Removed" in resp.json()["message"]

    # Ensure participant no longer present
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]


def test_signup_duplicate_returns_400():
    activity = "Soccer Club"
    email = f"pytest.{uuid4().hex}@example.com"

    # Sign up first time
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200

    # Sign up second time should fail
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 400
    assert resp.json().get("detail") == "Student already signed up for this activity"

    # Cleanup
    client.delete(f"/activities/{activity}/participants", params={"email": email})


def test_remove_nonexistent_returns_404():
    activity = "Art Club"
    email = f"pytest.{uuid4().hex}@example.com"

    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp.status_code == 404
    assert resp.json().get("detail") == "Student not found in this activity"

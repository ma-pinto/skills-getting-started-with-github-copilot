from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def _ensure_removed(activity: str, email: str):
    """Helper to remove a participant if present; ignore 404s to be idempotent."""
    encoded_activity = quote(activity, safe="")
    encoded_email = quote(email, safe="")
    client.delete(f"/activities/{encoded_activity}/participants/{encoded_email}")


def test_get_activities():
    # Arrange: nothing to set up

    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success():
    # Arrange
    activity = "Chess Club"
    email = "test_sign_up@example.com"
    encoded_activity = quote(activity, safe="")
    encoded_email = quote(email, safe="")
    _ensure_removed(activity, email)

    # Act
    resp = client.post(f"/activities/{encoded_activity}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert resp.json().get("message") == f"Signed up {email} for {activity}"

    # Cleanup
    del_resp = client.delete(f"/activities/{encoded_activity}/participants/{encoded_email}")
    assert del_resp.status_code == 200


def test_duplicate_signup_returns_400():
    # Arrange
    activity = "Chess Club"
    email = "test_duplicate@example.com"
    encoded_activity = quote(activity, safe="")
    encoded_email = quote(email, safe="")
    _ensure_removed(activity, email)
    first = client.post(f"/activities/{encoded_activity}/signup", params={"email": email})
    assert first.status_code == 200

    # Act
    second = client.post(f"/activities/{encoded_activity}/signup", params={"email": email})

    # Assert
    assert second.status_code == 400

    # Cleanup
    del_resp = client.delete(f"/activities/{encoded_activity}/participants/{encoded_email}")
    assert del_resp.status_code == 200


def test_remove_participant():
    # Arrange
    activity = "Chess Club"
    email = "test_remove@example.com"
    encoded_activity = quote(activity, safe="")
    encoded_email = quote(email, safe="")
    _ensure_removed(activity, email)
    signup = client.post(f"/activities/{encoded_activity}/signup", params={"email": email})
    assert signup.status_code == 200

    # Act
    rem = client.delete(f"/activities/{encoded_activity}/participants/{encoded_email}")

    # Assert
    assert rem.status_code == 200
    assert rem.json().get("message") == f"Removed {email} from {activity}"

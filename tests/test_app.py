from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    baseline = deepcopy(app_module.activities)
    monkeypatch.setattr(app_module, "activities", deepcopy(baseline))

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_available_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["participants"]


def test_signup_adds_student_when_spot_available(client):
    email = "newstudent@mergington.edu"

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in client.get("/activities").json()["Chess Club"]["participants"]


def test_signup_returns_400_for_duplicate_student(client):
    response = client.post("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})

    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_signup_returns_404_for_unknown_activity(client):
    response = client.post("/activities/Unknown Club/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_student(client):
    email = "michael@mergington.edu"

    response = client.delete("/activities/Chess Club/unregister", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert email not in client.get("/activities").json()["Chess Club"]["participants"]

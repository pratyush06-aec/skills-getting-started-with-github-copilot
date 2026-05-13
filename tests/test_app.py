"""
Pytest tests for the Mergington High School Management System API.
Tests follow the AAA (Arrange-Act-Assert) pattern.
"""

import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
original_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before and after each test."""
    activities.clear()
    activities.update(copy.deepcopy(original_activities))
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_payload():
    """GET /activities returns the activity payload with known activity keys."""
    # Arrange
    # (No setup needed)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_get_activities_includes_expected_fields():
    """GET /activities returns activities with expected structure."""
    # Arrange
    # (No setup needed)

    # Act
    response = client.get("/activities")

    # Assert
    data = response.json()
    for activity_name, activity_info in data.items():
        assert "description" in activity_info
        assert "schedule" in activity_info
        assert "max_participants" in activity_info
        assert "participants" in activity_info
        assert isinstance(activity_info["participants"], list)


def test_signup_for_activity_success():
    """POST /activities/{activity_name}/signup successfully signs up a new email."""
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    """POST /activities/{activity_name}/signup with duplicate email returns 400 error."""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already in initial participants

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_nonexistent_activity_returns_404():
    """POST /activities/{activity_name}/signup to non-existent activity returns 404."""
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "test@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_success():
    """DELETE /activities/{activity_name}/participant removes an existing participant."""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Known to be in initial participants

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participant",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_not_found_returns_404():
    """DELETE /activities/{activity_name}/participant for missing email returns 404."""
    # Arrange
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participant",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_from_nonexistent_activity_returns_404():
    """DELETE /activities/{activity_name}/participant to non-existent activity returns 404."""
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "test@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participant",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

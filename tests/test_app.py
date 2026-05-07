import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities(self, client):
        """Should return all activities"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity in expected_activities:
            assert activity in data

    def test_activity_has_required_fields(self, client):
        """Should return activities with all required fields"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        # Assert
        assert response.status_code == 200
        for field in required_fields:
            assert field in activity


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client, clear_activities):
        """Should successfully sign up a new student"""
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_duplicate_email(self, client):
        """Should reject signup if student already registered"""
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity(self, client):
        """Should return 404 for non-existent activity"""
        # Arrange
        fake_activity = "Nonexistent Club"
        test_email = "test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{fake_activity}/signup?email={test_email}"
        )
        
        # Assert
        assert response.status_code == 404

    def test_participant_added_to_list(self, client, clear_activities):
        """Should add participant to activity's participant list"""
        # Arrange
        activity_name = "Chess Club"
        test_email = "alice@mergington.edu"
        
        # Act
        client.post(f"/activities/{activity_name}/signup?email={test_email}")
        response = client.get("/activities")
        activity = response.json()[activity_name]
        
        # Assert
        assert test_email in activity["participants"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client, clear_activities):
        """Should successfully remove student from activity"""
        # Arrange
        activity_name = "Chess Club"
        test_email = "test@mergington.edu"
        client.post(f"/activities/{activity_name}/signup?email={test_email}")
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={test_email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_nonexistent_activity(self, client):
        """Should return 404 for non-existent activity"""
        # Arrange
        fake_activity = "Fake Club"
        test_email = "test@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{fake_activity}/unregister?email={test_email}"
        )
        
        # Assert
        assert response.status_code == 404

    def test_unregister_not_registered(self, client):
        """Should return 404 if student not registered"""
        # Arrange
        activity_name = "Chess Club"
        unregistered_email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={unregistered_email}"
        )
        
        # Assert
        assert response.status_code == 404

    def test_participant_removed_from_list(self, client, clear_activities):
        """Should remove participant from activity's participant list"""
        # Arrange
        activity_name = "Chess Club"
        test_email = "test@mergington.edu"
        client.post(f"/activities/{activity_name}/signup?email={test_email}")
        
        # Act
        client.delete(f"/activities/{activity_name}/unregister?email={test_email}")
        response = client.get("/activities")
        activity = response.json()[activity_name]
        
        # Assert
        assert test_email not in activity["participants"]

    def test_unregister_existing_participant(self, client, clear_activities):
        """Should allow removing an originally registered participant"""
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={existing_email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

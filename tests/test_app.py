import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_list(self):
        """Arrange: Have a running app
        Act: Call GET /activities
        Assert: Should return 200 and a list of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0

    def test_get_activities_has_required_fields(self):
        """Arrange: Have a running app
        Act: Call GET /activities
        Assert: Each activity should have required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for name, details in activities.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity_success(self):
        """Arrange: Have an activity and valid email
        Act: Sign up for an activity
        Assert: Should return 200 and success message"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@example.com"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@example.com" in data["message"]

    def test_signup_for_nonexistent_activity(self):
        """Arrange: Have an invalid activity name
        Act: Try to sign up for non-existent activity
        Assert: Should return 404"""
        response = client.post(
            "/activities/NonExistent/signup?email=test@example.com"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_email(self):
        """Arrange: Have a student already signed up
        Act: Try to sign up same email again
        Assert: Should return 400 error"""
        # First signup
        client.post("/activities/Chess%20Club/signup?email=duplicate@example.com")
        
        # Try duplicate signup
        response = client.post(
            "/activities/Chess%20Club/signup?email=duplicate@example.com"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_activity_full(self):
        """Arrange: Have a full activity
        Act: Try to sign up for full activity
        Assert: Should return 400 error"""
        activity_name = "Chess%20Club"
        
        # Fill up the activity
        for i in range(12):  # Chess Club has max 12 participants
            response = client.post(
                f"/activities/{activity_name}/signup?email=student{i}@example.com"
            )
            if response.status_code != 200:
                break
        
        # Try to add one more
        response = client.post(
            f"/activities/{activity_name}/signup?email=extra@example.com"
        )
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self):
        """Arrange: Have a student signed up
        Act: Unregister the student
        Assert: Should return 200 and success message"""
        email = "unregister@example.com"
        activity = "Programming%20Class"
        
        # Sign up first
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Unregister
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_not_signed_up(self):
        """Arrange: Have a student not signed up
        Act: Try to unregister
        Assert: Should return 400 error"""
        response = client.delete(
            "/activities/Gym%20Class/unregister?email=nothere@example.com"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_nonexistent_activity(self):
        """Arrange: Have an invalid activity name
        Act: Try to unregister from non-existent activity
        Assert: Should return 404"""
        response = client.delete(
            "/activities/Fake/unregister?email=test@example.com"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_index(self):
        """Arrange: Have a running app
        Act: Call GET /
        Assert: Should redirect to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

import pytest
from fastapi.testclient import TestClient
from src.app import app

# Fixture for TestClient (reusable across tests)
@pytest.fixture
def client():
    return TestClient(app)

# Test root endpoint
def test_root_redirect(client):
    # Arrange
    # No special setup needed

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200  # Follows redirect to static file

# Test get_activities endpoint
def test_get_activities(client):
    # Arrange
    # No special setup needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data  # Check a sample activity
    assert "participants" in data["Chess Club"]

# Test signup endpoint - success
def test_signup_success(client):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert "Signed up newstudent@mergington.edu for Chess Club" in response.json()["message"]
    # Verify state change
    activities_response = client.get("/activities")
    assert email in activities_response.json()["Chess Club"]["participants"]

# Test signup endpoint - activity not found
def test_signup_activity_not_found(client):
    # Arrange
    email = "test@mergington.edu"

    # Act
    response = client.post("/activities/NonExistent/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

# Test signup endpoint - already signed up
def test_signup_already_signed_up(client):
    # Arrange
    email = "duplicate@mergington.edu"
    # First signup
    client.post("/activities/Chess Club/signup", params={"email": email})

    # Act
    # Duplicate attempt
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert "Student is already signed up" in response.json()["detail"]

# Test unregister endpoint - success
def test_unregister_success(client):
    # Arrange
    email = "removeme@mergington.edu"
    # Signup first
    client.post("/activities/Programming Class/signup", params={"email": email})

    # Act
    response = client.delete(f"/activities/Programming Class/participants/{email}")

    # Assert
    assert response.status_code == 200
    assert "Unregistered removeme@mergington.edu from Programming Class" in response.json()["message"]
    # Verify state change
    activities_response = client.get("/activities")
    assert email not in activities_response.json()["Programming Class"]["participants"]

# Test unregister endpoint - activity not found
def test_unregister_activity_not_found(client):
    # Arrange
    email = "test@mergington.edu"

    # Act
    response = client.delete(f"/activities/NonExistent/participants/{email}")

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

# Test unregister endpoint - not signed up
def test_unregister_not_signed_up(client):
    # Arrange
    email = "notsignedup@mergington.edu"

    # Act
    response = client.delete(f"/activities/Chess Club/participants/{email}")

    # Assert
    assert response.status_code == 400
    assert "Student not signed up" in response.json()["detail"]
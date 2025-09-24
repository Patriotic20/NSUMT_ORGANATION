import pytest

def test_create_user(client):
    response = client.post(
        "/auth/register",
        json={"username": "admin", "password": "admin"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Register successfully"}
    


    
# def test_login_user(client):
#     # First, create a user to log in with
#     register_response = client.post(
#         "/auth/register",
#         json={"username": "testuser", "password": "testpassword"}
#     )
#     assert register_response.status_code == 200

#     # Then, attempt to log in with that user's credentials
#     login_response = client.post(
#         "/auth/login",
#         json={"username": "testuser", "password": "testpassword"}
#     )
    
#     # Assert the login was successful
#     assert login_response.status_code == 200
#     assert "access_token" in login_response.json()
#     assert login_response.json()["token_type"] == "bearer"


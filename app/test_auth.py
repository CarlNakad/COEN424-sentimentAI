import httpx
import pytest

BASE_URL = "http://127.0.0.1:8000"

def test_token_authentication():
    # Step 1: Get a token
    response = httpx.post(f"{BASE_URL}/token", data={"username": "bash", "password": "1234"})
    assert response.status_code == 200
    token = response.json().get("access_token")
    assert token is not None

    # Step 2: Access a protected route with the token
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get(f"{BASE_URL}/users/me", headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["username"] == "johndoe"

    # Step 3: Access a protected route without the token
    response = httpx.get(f"{BASE_URL}/users/me")
    assert response.status_code == 401

if __name__ == "__main__":
    pytest.main()
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from main import app

client = TestClient(app)

def test_auth_start_exists():
    with patch("api.v1.endpoints.auth.get_supabase") as mock_get_supabase:
        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        
        # Mock response for existing user
        mock_response = MagicMock()
        mock_response.data = [{"id": "123", "password_hash": "hashed"}]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        response = client.post("/api/v1/auth/start", json={"email": "test@example.com"})
        assert response.status_code == 200
        assert response.json() == {"exists": True, "next": "password"}

def test_auth_start_new():
    with patch("api.v1.endpoints.auth.get_supabase") as mock_get_supabase:
        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        
        # Mock response for non-existing user
        mock_response = MagicMock()
        mock_response.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        response = client.post("/api/v1/auth/start", json={"email": "new@example.com"})
        assert response.status_code == 200
        assert response.json() == {"exists": False, "next": "create_account"}

def test_signup_success():
    with patch("api.v1.endpoints.auth.get_supabase") as mock_get_supabase, \
         patch("api.v1.endpoints.auth.get_password_hash") as mock_hash, \
         patch("api.v1.endpoints.auth.get_redis") as mock_get_redis, \
         patch("api.v1.endpoints.auth.random.randint") as mock_randint:
        
        # Mock Redis async context manager
        mock_redis_store = MagicMock()
        mock_redis_store.setex = MagicMock(return_value=True)
        mock_async_context_manager = MagicMock()
        mock_async_context_manager.__aenter__.return_value = mock_redis_store
        mock_get_redis.return_value = mock_async_context_manager
        
        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        mock_hash.return_value = "hashed_secret"
        mock_randint.return_value = 123456
        
        # Mock username check (empty = unique)
        mock_user_check = MagicMock()
        mock_user_check.data = []
        
        # Mock insert response
        mock_insert_res = MagicMock()
        mock_insert_res.data = [{"id": "new_user_uuid"}]
        
        # Setup chain for select (username check) and insert
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_user_check
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_insert_res
        
        payload = {
            "email": "new@example.com",
            "password": "secretpassword",
            "confirmPassword": "secretpassword",
            "username": "newuser",
            "fullName": "New User",
            "dob": "2000-01-01",
            "newsletterOptIn": True
        }
        
        response = client.post("/api/v1/auth/signup", json=payload)
        assert response.status_code == 201
        assert "user_id" in response.json()
        assert response.json()["message"] == "User created successfully. Please check your email for confirmation code."
        assert response.json()["next"] == "confirm_email"

def test_verify_otp_success():
    with patch("api.v1.endpoints.auth.get_supabase") as mock_get_supabase, \
         patch("api.v1.endpoints.auth.get_redis") as mock_get_redis, \
         patch("api.v1.endpoints.auth.create_access_token") as mock_token:
        
        # Mock Redis async context manager
        mock_redis_store = MagicMock()
        mock_redis_store.get = MagicMock(return_value="123456")
        mock_redis_store.delete = MagicMock(return_value=True)
        mock_async_context_manager = MagicMock()
        mock_async_context_manager.__aenter__.return_value = mock_redis_store
        mock_get_redis.return_value = mock_async_context_manager
        
        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        mock_token.return_value = "fake_jwt_token"
        
        # Mock user lookup response for finding user by email
        mock_user_lookup_response = MagicMock()
        mock_user_lookup_response.data = [{"id": "user_uuid"}]
        
        # Mock user data response for getting user details
        mock_user_data_response = MagicMock()
        mock_user_data_response.data = [{"id": "user_uuid", "email": "test@example.com", "username": "testuser"}]
        
        # Mock the update operation response
        mock_update_response = MagicMock()
        
        # Setup the mock chain properly
        # First call: select user by email
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_user_lookup_response
        
        # Second call: update user email_confirmed
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_update_response
        
        # Third call: select user data for response
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_user_data_response
        
        payload = {
            "email": "test@example.com",
            "code": "123456"
        }
        
        response = client.post("/api/v1/auth/verify-otp", json=payload)
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["message"] == "Email verified successfully"

def test_check_username_availability():
    with patch("api.v1.endpoints.auth.get_supabase") as mock_get_supabase:
        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        
        # Mock response for username check (empty = available)
        mock_response = MagicMock()
        mock_response.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        response = client.get("/api/v1/auth/check-username/testuser")
        assert response.status_code == 200
        assert response.json() == {"available": True}
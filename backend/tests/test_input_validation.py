"""
Input Validation and Error Handling Tests
Comprehensive tests for API input validation and consistent error responses
"""
import pytest
from datetime import date, datetime
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.main import app
from app.core.database import get_session, create_db_and_tables, engine
from app.core.security import get_password_hash
from app.models.user import User, UserRole


@pytest.fixture(scope="module")
def test_db():
    """Create test database"""
    create_db_and_tables()
    yield


@pytest.fixture(scope="module")
def client(test_db):
    """Create test client"""
    def get_test_session():
        with Session(engine) as session:
            yield session
    
    app.dependency_overrides[get_session] = get_test_session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def auth_token(client):
    """Get authentication token for testing"""
    # Create test user
    with Session(engine) as session:
        existing_user = session.query(User).filter(User.username == "test_validation_user").first()
        if not existing_user:
            test_user = User(
                username="test_validation_user",
                email="validation@test.com",
                full_name="Validation Test User",
                role=UserRole.ADMIN,
                hashed_password=get_password_hash("test123"),
                is_active=True
            )
            session.add(test_user)
            session.commit()
    
    # Login to get token
    response = client.post(
        "/auth/login",
        data={"username": "test_validation_user", "password": "test123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


class TestInputValidation:
    """Test input validation across all endpoints"""
    
    def test_case_creation_validation(self, client, auth_token):
        """Test case creation input validation"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Test missing required fields
        invalid_cases = [
            # Missing case_number
            {
                "title": "Test Case",
                "case_type": "civil",
                "synopsis": "Test synopsis",
                "filing_date": date.today().isoformat(),
                "priority": "medium"
            },
            # Invalid case_type
            {
                "case_number": "VAL/2024/001",
                "title": "Test Case",
                "case_type": "invalid_type",
                "synopsis": "Test synopsis", 
                "filing_date": date.today().isoformat(),
                "priority": "medium"
            },
            # Invalid priority
            {
                "case_number": "VAL/2024/002",
                "title": "Test Case",
                "case_type": "civil",
                "synopsis": "Test synopsis",
                "filing_date": date.today().isoformat(),
                "priority": "invalid_priority"
            },
            # Invalid date format
            {
                "case_number": "VAL/2024/003",
                "title": "Test Case",
                "case_type": "civil",
                "synopsis": "Test synopsis",
                "filing_date": "invalid-date",
                "priority": "medium"
            },
            # Future filing date
            {
                "case_number": "VAL/2024/004",
                "title": "Test Case",
                "case_type": "civil",
                "synopsis": "Test synopsis",
                "filing_date": "2025-12-31",
                "priority": "medium"
            },
            # Negative duration
            {
                "case_number": "VAL/2024/005",
                "title": "Test Case",
                "case_type": "civil",
                "synopsis": "Test synopsis",
                "filing_date": date.today().isoformat(),
                "priority": "medium",
                "estimated_duration_minutes": -30
            }
        ]
        
        for i, invalid_case in enumerate(invalid_cases):
            response = client.post("/cases/", json=invalid_case, headers=headers)
            assert response.status_code == 422, f"Invalid case {i} should return 422"
            
            # Check error response format
            error_data = response.json()
            assert "detail" in error_data, f"Error response {i} should have 'detail' field"
            
            if isinstance(error_data["detail"], list):
                # Pydantic validation errors
                for error in error_data["detail"]:
                    assert "loc" in error, "Validation error should have 'loc' field"
                    assert "msg" in error, "Validation error should have 'msg' field"
                    assert "type" in error, "Validation error should have 'type' field"
    
    def test_user_creation_validation(self, client, auth_token):
        """Test user creation input validation"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        invalid_users = [
            # Missing email
            {
                "username": "testuser",
                "full_name": "Test User",
                "role": "clerk",
                "password": "password123"
            },
            # Invalid email format
            {
                "username": "testuser2",
                "email": "invalid-email",
                "full_name": "Test User",
                "role": "clerk", 
                "password": "password123"
            },
            # Invalid role
            {
                "username": "testuser3",
                "email": "test@example.com",
                "full_name": "Test User",
                "role": "invalid_role",
                "password": "password123"
            },
            # Short password
            {
                "username": "testuser4",
                "email": "test2@example.com",
                "full_name": "Test User",
                "role": "clerk",
                "password": "123"
            },
            # Duplicate username (if we create one first)
            {
                "username": "test_validation_user",
                "email": "test3@example.com",
                "full_name": "Test User",
                "role": "clerk",
                "password": "password123"
            }
        ]
        
        for i, invalid_user in enumerate(invalid_users):
            response = client.post("/auth/register", json=invalid_user, headers=headers)
            assert response.status_code in [422, 400], f"Invalid user {i} should return 422 or 400"
    
    def test_schedule_allocation_validation(self, client, auth_token):
        """Test schedule allocation input validation"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        invalid_params = [
            # Invalid date format
            {"start_date": "invalid-date", "num_days": 1},
            # Negative days
            {"start_date": date.today().isoformat(), "num_days": -1},
            # Zero days
            {"start_date": date.today().isoformat(), "num_days": 0},
            # Too many days
            {"start_date": date.today().isoformat(), "num_days": 100},
            # Past date
            {"start_date": "2020-01-01", "num_days": 1}
        ]
        
        for i, params in enumerate(invalid_params):
            response = client.post("/schedule/allocate", params=params, headers=headers)
            assert response.status_code in [422, 400], f"Invalid schedule params {i} should return 422 or 400"
    
    def test_bench_creation_validation(self, client, auth_token):
        """Test bench creation input validation"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        invalid_benches = [
            # Missing name
            {
                "court_number": "TEST-1",
                "capacity": 50
            },
            # Missing court_number
            {
                "name": "Test Court",
                "capacity": 50
            },
            # Invalid capacity
            {
                "name": "Test Court",
                "court_number": "TEST-2",
                "capacity": -10
            },
            # Zero capacity
            {
                "name": "Test Court", 
                "court_number": "TEST-3",
                "capacity": 0
            },
            # Excessive capacity
            {
                "name": "Test Court",
                "court_number": "TEST-4",
                "capacity": 10000
            }
        ]
        
        for i, invalid_bench in enumerate(invalid_benches):
            response = client.post("/benches/", json=invalid_bench, headers=headers)
            assert response.status_code == 422, f"Invalid bench {i} should return 422"


class TestErrorResponseFormat:
    """Test consistent error response formatting"""
    
    def test_validation_error_format(self, client, auth_token):
        """Test that validation errors have consistent format"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Trigger validation error
        invalid_case = {
            "title": "Test Case",
            "case_type": "invalid_type",
            "synopsis": "Test synopsis"
        }
        
        response = client.post("/cases/", json=invalid_case, headers=headers)
        assert response.status_code == 422
        
        error_data = response.json()
        assert "detail" in error_data
        
        # Should be list of validation errors
        if isinstance(error_data["detail"], list):
            for error in error_data["detail"]:
                assert isinstance(error, dict)
                assert "loc" in error
                assert "msg" in error
                assert "type" in error
                assert isinstance(error["loc"], list)
                assert isinstance(error["msg"], str)
                assert isinstance(error["type"], str)
    
    def test_authentication_error_format(self, client):
        """Test authentication error format"""
        # Missing token
        response = client.get("/auth/me")
        assert response.status_code in [401, 403]
        
        # Invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 401
        
        error_data = response.json()
        assert "detail" in error_data
        assert isinstance(error_data["detail"], str)
    
    def test_authorization_error_format(self, client):
        """Test authorization error format for insufficient permissions"""
        # Create public user token
        with Session(engine) as session:
            existing_user = session.query(User).filter(User.username == "test_public_user").first()
            if not existing_user:
                public_user = User(
                    username="test_public_user",
                    email="public@test.com",
                    full_name="Public Test User",
                    role=UserRole.PUBLIC,
                    hashed_password=get_password_hash("test123"),
                    is_active=True
                )
                session.add(public_user)
                session.commit()
        
        # Login as public user
        response = client.post(
            "/auth/login",
            data={"username": "test_public_user", "password": "test123"}
        )
        assert response.status_code == 200
        public_token = response.json()["access_token"]
        
        # Try to access restricted endpoint
        headers = {"Authorization": f"Bearer {public_token}"}
        response = client.post("/cases/", json={}, headers=headers)
        assert response.status_code == 403
        
        error_data = response.json()
        assert "detail" in error_data
        assert isinstance(error_data["detail"], str)
    
    def test_not_found_error_format(self, client, auth_token):
        """Test not found error format"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Try to get non-existent case
        response = client.get("/cases/99999", headers=headers)
        assert response.status_code == 404
        
        error_data = response.json()
        assert "detail" in error_data
        assert isinstance(error_data["detail"], str)
    
    def test_business_logic_error_format(self, client, auth_token):
        """Test business logic error format"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Try to schedule with no benches available
        response = client.post(
            "/schedule/allocate",
            params={"start_date": date.today().isoformat(), "num_days": 1},
            headers=headers
        )
        
        # Should handle gracefully with proper error format
        if response.status_code >= 400:
            error_data = response.json()
            assert "detail" in error_data
            assert isinstance(error_data["detail"], str)


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_extremely_long_inputs(self, client, auth_token):
        """Test handling of extremely long input strings"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Very long title
        long_title = "A" * 10000
        long_case = {
            "case_number": "LONG/2024/001",
            "title": long_title,
            "case_type": "civil",
            "synopsis": "Test case with long title",
            "filing_date": date.today().isoformat(),
            "priority": "medium"
        }
        
        response = client.post("/cases/", json=long_case, headers=headers)
        # Should either accept (if no length limit) or reject with validation error
        assert response.status_code in [200, 201, 422]
    
    def test_special_characters_in_input(self, client, auth_token):
        """Test handling of special characters"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        special_chars_case = {
            "case_number": "SPEC/2024/001",
            "title": "Test Case with Special Chars: <>&\"'",
            "case_type": "civil",
            "synopsis": "Synopsis with special chars: <>{}[]()&*%$#@!",
            "filing_date": date.today().isoformat(),
            "priority": "medium"
        }
        
        response = client.post("/cases/", json=special_chars_case, headers=headers)
        # Should handle special characters safely
        assert response.status_code in [200, 201, 422]
    
    def test_unicode_characters(self, client, auth_token):
        """Test handling of Unicode characters"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        unicode_case = {
            "case_number": "UNI/2024/001",
            "title": "Test Case with Unicode: 中文 العربية русский",
            "case_type": "civil",
            "synopsis": "Synopsis with emoji: 📚⚖️🏛️",
            "filing_date": date.today().isoformat(),
            "priority": "medium"
        }
        
        response = client.post("/cases/", json=unicode_case, headers=headers)
        # Should handle Unicode safely
        assert response.status_code in [200, 201, 422]
    
    def test_sql_injection_attempts(self, client, auth_token):
        """Test SQL injection protection"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        sql_injection_attempts = [
            "'; DROP TABLE cases; --",
            "' OR '1'='1",
            "'; INSERT INTO cases VALUES (1); --",
            "' UNION SELECT * FROM users --"
        ]
        
        for injection in sql_injection_attempts:
            malicious_case = {
                "case_number": injection,
                "title": f"Test Case {injection}",
                "case_type": "civil",
                "synopsis": injection,
                "filing_date": date.today().isoformat(),
                "priority": "medium"
            }
            
            response = client.post("/cases/", json=malicious_case, headers=headers)
            # Should safely handle or reject, but not crash
            assert response.status_code in [200, 201, 400, 422]
    
    def test_xss_attempts(self, client, auth_token):
        """Test XSS protection"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        xss_attempts = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "onload=alert('xss')"
        ]
        
        for xss in xss_attempts:
            malicious_case = {
                "case_number": f"XSS/2024/{hash(xss) % 1000}",
                "title": f"Test Case {xss}",
                "case_type": "civil", 
                "synopsis": xss,
                "filing_date": date.today().isoformat(),
                "priority": "medium"
            }
            
            response = client.post("/cases/", json=malicious_case, headers=headers)
            # Should safely handle malicious input
            assert response.status_code in [200, 201, 400, 422]


class TestConcurrentRequestHandling:
    """Test handling of concurrent requests"""
    
    def test_concurrent_case_creation(self, client, auth_token):
        """Test concurrent case creation doesn't cause issues"""
        import threading
        import time
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        results = []
        
        def create_case(case_num):
            case_data = {
                "case_number": f"CONC/2024/{case_num:03d}",
                "title": f"Concurrent Test Case {case_num}",
                "case_type": "civil",
                "synopsis": f"Concurrent test case {case_num}",
                "filing_date": date.today().isoformat(),
                "priority": "medium"
            }
            
            response = client.post("/cases/", json=case_data, headers=headers)
            results.append((case_num, response.status_code))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_case, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(results) == 5
        for case_num, status_code in results:
            assert status_code in [200, 201, 400, 422], f"Case {case_num} had unexpected status {status_code}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

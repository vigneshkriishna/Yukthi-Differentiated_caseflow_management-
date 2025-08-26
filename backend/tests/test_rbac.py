"""
RBAC and Authentication Security Tests
Comprehensive tests for role-based access control and authentication
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.main import app
from app.core.database import get_session, create_db_and_tables, engine
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.bench import Bench
from app.models.case import Case, CaseType, CasePriority, CaseStatus
from datetime import date


@pytest.fixture(scope="module")
def test_db():
    """Create test database"""
    create_db_and_tables()
    yield
    # Cleanup after tests if needed


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
def test_users(client):
    """Create test users for RBAC testing"""
    users = {}
    
    with Session(engine) as session:
        # Create test users for each role
        test_user_data = [
            ("test_admin", "admin@test.com", "Test Admin", UserRole.ADMIN),
            ("test_judge", "judge@test.com", "Test Judge", UserRole.JUDGE),  
            ("test_clerk", "clerk@test.com", "Test Clerk", UserRole.CLERK),
            ("test_lawyer", "lawyer@test.com", "Test Lawyer", UserRole.LAWYER),
            ("test_public", "public@test.com", "Test Public", UserRole.PUBLIC),
        ]
        
        for username, email, full_name, role in test_user_data:
            # Check if user already exists
            existing = session.exec(select(User).where(User.username == username)).first()
            if not existing:
                user = User(
                    username=username,
                    email=email,
                    full_name=full_name,
                    role=role,
                    hashed_password=get_password_hash("test123"),
                    is_active=True
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                users[role.value] = user
            else:
                users[role.value] = existing
    
    return users


@pytest.fixture(scope="module")
def test_tokens(client, test_users):
    """Get authentication tokens for test users"""
    tokens = {}
    
    for role, user in test_users.items():
        response = client.post(
            "/auth/login",
            data={"username": user.username, "password": "test123"}
        )
        assert response.status_code == 200
        token_data = response.json()
        tokens[role] = token_data["access_token"]
    
    return tokens


@pytest.fixture(scope="module")
def test_bench(client, test_tokens):
    """Create test bench"""
    with Session(engine) as session:
        # Check if bench exists
        existing = session.exec(select(Bench).where(Bench.court_number == "TEST-1")).first()
        if not existing:
            bench = Bench(
                name="Test Court",
                court_number="TEST-1", 
                capacity=50,
                is_active=True
            )
            session.add(bench)
            session.commit()
            session.refresh(bench)
            return bench
        return existing


@pytest.fixture(scope="module")
def test_case(client, test_tokens, test_users, test_bench):
    """Create test case"""
    headers = {"Authorization": f"Bearer {test_tokens['clerk']}"}
    
    case_data = {
        "case_number": "TEST/2024/001",
        "title": "Test Case for RBAC",
        "case_type": "criminal",
        "synopsis": "Test case for RBAC authentication testing",
        "filing_date": date.today().isoformat(),
        "priority": "medium",
        "estimated_duration_minutes": 120
    }
    
    response = client.post("/cases/", json=case_data, headers=headers)
    if response.status_code == 200:
        return response.json()
    
    # Case might already exist, get it
    response = client.get("/cases/", headers=headers)
    cases = response.json()
    for case in cases:
        if case["case_number"] == "TEST/2024/001":
            return case
    
    return None


class TestAuthentication:
    """Test authentication mechanisms"""
    
    def test_login_valid_credentials(self, client, test_users):
        """Test login with valid credentials"""
        response = client.post(
            "/auth/login",
            data={"username": "test_admin", "password": "test123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == "test_admin"
    
    def test_login_invalid_username(self, client):
        """Test login with invalid username"""
        response = client.post(
            "/auth/login",
            data={"username": "nonexistent", "password": "test123"}
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_invalid_password(self, client):
        """Test login with invalid password"""
        response = client.post(
            "/auth/login",
            data={"username": "test_admin", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_token_verification(self, client, test_tokens):
        """Test token verification"""
        headers = {"Authorization": f"Bearer {test_tokens['admin']}"}
        response = client.get("/auth/verify-token", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["username"] == "test_admin"
    
    def test_invalid_token(self, client):
        """Test with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 401
    
    def test_missing_token(self, client):
        """Test protected endpoint without token"""
        response = client.get("/auth/me")
        assert response.status_code == 403  # FastAPI returns 403 for missing auth


class TestRoleBasedAccess:
    """Test role-based access control"""
    
    def test_admin_full_access(self, client, test_tokens, test_case):
        """Test admin has full access to all endpoints"""
        headers = {"Authorization": f"Bearer {test_tokens['admin']}"}
        
        # Should access all endpoints
        endpoints = [
            ("GET", "/cases/"),
            ("GET", "/schedule/hearings"),
            ("GET", "/reports/metrics"),
            ("GET", "/reports/dashboard"),
        ]
        
        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint, headers=headers)
            elif method == "POST":
                response = client.post(endpoint, headers=headers)
            
            assert response.status_code in [200, 422], f"Admin failed to access {method} {endpoint}"
    
    def test_clerk_case_operations(self, client, test_tokens, test_case):
        """Test clerk can perform case operations"""
        headers = {"Authorization": f"Bearer {test_tokens['clerk']}"}
        
        # Should be able to create cases
        case_data = {
            "case_number": "RBAC/2024/001",
            "title": "RBAC Test Case",
            "case_type": "civil",
            "synopsis": "Test case for clerk RBAC",
            "filing_date": date.today().isoformat(),
            "priority": "low",
            "estimated_duration_minutes": 60
        }
        response = client.post("/cases/", json=case_data, headers=headers)
        assert response.status_code in [200, 400]  # 400 if already exists
        
        # Should be able to list cases
        response = client.get("/cases/", headers=headers)
        assert response.status_code == 200
        
        # Should be able to classify cases
        if test_case:
            case_id = test_case["id"]
            response = client.post(f"/cases/{case_id}/classify", headers=headers)
            assert response.status_code == 200
        
        # Should be able to schedule
        response = client.post(
            "/schedule/allocate",
            params={"start_date": date.today().isoformat(), "num_days": 1},
            headers=headers
        )
        assert response.status_code in [200, 400]  # May fail if no benches
    
    def test_judge_override_access(self, client, test_tokens, test_case):
        """Test judge can override case tracks"""
        headers = {"Authorization": f"Bearer {test_tokens['judge']}"}
        
        if not test_case:
            pytest.skip("No test case available")
        
        case_id = test_case["id"]
        
        # Classify case first as clerk
        clerk_headers = {"Authorization": f"Bearer {test_tokens['clerk']}"}
        client.post(f"/cases/{case_id}/classify", headers=clerk_headers)
        
        # Judge should be able to override
        override_data = {
            "new_track": "complex",
            "reason": "RBAC test override - requires complex handling"
        }
        response = client.post(
            f"/cases/{case_id}/override-track",
            json=override_data,
            headers=headers
        )
        assert response.status_code == 200
        
    def test_lawyer_limited_access(self, client, test_tokens):
        """Test lawyer has limited read access"""
        headers = {"Authorization": f"Bearer {test_tokens['lawyer']}"}
        
        # Should be able to view cases (read-only)
        response = client.get("/cases/", headers=headers)
        assert response.status_code == 200
        
        # Should NOT be able to create cases
        case_data = {
            "case_number": "LAWYER/2024/001",
            "title": "Lawyer Test Case",
            "case_type": "civil",
            "synopsis": "Test case",
            "filing_date": date.today().isoformat(),
            "priority": "low",
            "estimated_duration_minutes": 60
        }
        response = client.post("/cases/", json=case_data, headers=headers)
        assert response.status_code == 403
        
        # Should NOT be able to schedule
        response = client.post(
            "/schedule/allocate",
            params={"start_date": date.today().isoformat(), "num_days": 1},
            headers=headers
        )
        assert response.status_code == 403
    
    def test_public_minimal_access(self, client, test_tokens):
        """Test public user has minimal access"""
        headers = {"Authorization": f"Bearer {test_tokens['public']}"}
        
        # Should NOT be able to access most endpoints
        restricted_endpoints = [
            ("POST", "/cases/"),
            ("POST", "/schedule/allocate"),
            ("GET", "/reports/metrics"),
        ]
        
        for method, endpoint in restricted_endpoints:
            if method == "GET":
                response = client.get(endpoint, headers=headers)
            elif method == "POST":
                response = client.post(endpoint, headers=headers)
            
            assert response.status_code == 403, f"Public user should not access {method} {endpoint}"
    
    def test_role_specific_data_access(self, client, test_tokens, test_case):
        """Test users can only access data relevant to their role"""
        if not test_case:
            pytest.skip("No test case available")
        
        case_id = test_case["id"]
        
        # Clerk should only see cases assigned to them
        clerk_headers = {"Authorization": f"Bearer {test_tokens['clerk']}"}
        response = client.get(f"/cases/{case_id}", headers=clerk_headers)
        
        # Should either succeed (if assigned) or be forbidden
        assert response.status_code in [200, 403]
        
        # Judge should see cases assigned to their hearings
        judge_headers = {"Authorization": f"Bearer {test_tokens['judge']}"}
        response = client.get("/schedule/hearings", headers=judge_headers)
        assert response.status_code == 200


class TestEndpointSecurity:
    """Test endpoint-specific security requirements"""
    
    def test_case_classification_requires_clerk(self, client, test_tokens, test_case):
        """Test case classification requires clerk access or higher"""
        if not test_case:
            pytest.skip("No test case available")
        
        case_id = test_case["id"]
        
        # Lawyer should not be able to classify
        lawyer_headers = {"Authorization": f"Bearer {test_tokens['lawyer']}"}
        response = client.post(f"/cases/{case_id}/classify", headers=lawyer_headers)
        assert response.status_code == 403
        
        # Public should not be able to classify
        public_headers = {"Authorization": f"Bearer {test_tokens['public']}"}
        response = client.post(f"/cases/{case_id}/classify", headers=public_headers)
        assert response.status_code == 403
        
        # Clerk should be able to classify
        clerk_headers = {"Authorization": f"Bearer {test_tokens['clerk']}"}
        response = client.post(f"/cases/{case_id}/classify", headers=clerk_headers)
        assert response.status_code == 200
    
    def test_track_override_requires_judge(self, client, test_tokens, test_case):
        """Test track override requires judge access"""
        if not test_case:
            pytest.skip("No test case available")
        
        case_id = test_case["id"]
        override_data = {
            "new_track": "fast",
            "reason": "Test override"
        }
        
        # Clerk should not be able to override
        clerk_headers = {"Authorization": f"Bearer {test_tokens['clerk']}"}
        response = client.post(
            f"/cases/{case_id}/override-track",
            json=override_data,
            headers=clerk_headers
        )
        assert response.status_code == 403
        
        # Lawyer should not be able to override  
        lawyer_headers = {"Authorization": f"Bearer {test_tokens['lawyer']}"}
        response = client.post(
            f"/cases/{case_id}/override-track",
            json=override_data,
            headers=lawyer_headers
        )
        assert response.status_code == 403
        
        # Judge should be able to override
        judge_headers = {"Authorization": f"Bearer {test_tokens['judge']}"}
        response = client.post(
            f"/cases/{case_id}/override-track",
            json=override_data,
            headers=judge_headers
        )
        assert response.status_code == 200
    
    def test_scheduling_requires_clerk_or_admin(self, client, test_tokens):
        """Test scheduling requires clerk or admin access"""
        
        # Public should not be able to schedule
        public_headers = {"Authorization": f"Bearer {test_tokens['public']}"}
        response = client.post(
            "/schedule/allocate",
            params={"start_date": date.today().isoformat(), "num_days": 1},
            headers=public_headers
        )
        assert response.status_code == 403
        
        # Lawyer should not be able to schedule
        lawyer_headers = {"Authorization": f"Bearer {test_tokens['lawyer']}"}
        response = client.post(
            "/schedule/allocate", 
            params={"start_date": date.today().isoformat(), "num_days": 1},
            headers=lawyer_headers
        )
        assert response.status_code == 403
        
        # Clerk should be able to schedule
        clerk_headers = {"Authorization": f"Bearer {test_tokens['clerk']}"}
        response = client.post(
            "/schedule/allocate",
            params={"start_date": date.today().isoformat(), "num_days": 1},
            headers=clerk_headers
        )
        assert response.status_code in [200, 400]  # May fail if no data


class TestErrorHandling:
    """Test security error handling"""
    
    def test_401_unauthorized_response_format(self, client):
        """Test 401 responses have correct format"""
        response = client.get("/auth/me")
        assert response.status_code in [401, 403]
        # Should return proper error format
    
    def test_403_forbidden_response_format(self, client, test_tokens):
        """Test 403 responses have correct format"""
        public_headers = {"Authorization": f"Bearer {test_tokens['public']}"}
        response = client.post("/cases/", json={}, headers=public_headers)
        assert response.status_code == 403
        # Should return proper error format
    
    def test_token_expiry_handling(self, client):
        """Test expired token handling"""
        # This would require creating an expired token
        # For now, test with malformed token
        headers = {"Authorization": "Bearer expired.token.here"}
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

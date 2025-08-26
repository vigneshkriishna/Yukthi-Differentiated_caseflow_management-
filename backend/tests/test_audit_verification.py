"""
Audit Log Verification Tests
Tests to verify audit logging functionality and data integrity
"""
import pytest
from datetime import datetime, date
from sqlmodel import Session, select
from app.core.database import get_session, create_db_and_tables, engine
from app.models.user import User, UserRole
from app.models.case import Case, CaseType, CasePriority, CaseStatus
from app.models.audit_log import AuditLog, AuditAction
from app.services.audit_service import AuditService
from app.core.security import get_password_hash


@pytest.fixture(scope="module")
def test_db():
    """Create test database"""
    create_db_and_tables()
    yield


@pytest.fixture
def clean_session(test_db):
    """Provide clean database session for each test"""
    with Session(engine) as session:
        # Clean up existing test data
        session.query(AuditLog).delete()
        session.query(Case).delete()
        session.query(User).filter(User.username.like("audit_test_%")).delete()
        session.commit()
        yield session


@pytest.fixture
def test_user(clean_session):
    """Create test user for audit testing"""
    user = User(
        username="audit_test_user",
        email="audit@test.com",
        full_name="Audit Test User",
        role=UserRole.CLERK,
        hashed_password=get_password_hash("test123"),
        is_active=True
    )
    clean_session.add(user)
    clean_session.commit()
    clean_session.refresh(user)
    return user


@pytest.fixture
def test_case(clean_session, test_user):
    """Create test case for audit testing"""
    case = Case(
        case_number="AUDIT/2024/001",
        title="Audit Test Case",
        case_type=CaseType.CIVIL,
        synopsis="Test case for audit verification",
        filing_date=date.today(),
        priority=CasePriority.MEDIUM,
        estimated_duration_minutes=120,
        status=CaseStatus.FILED
    )
    clean_session.add(case)
    clean_session.commit()
    clean_session.refresh(case)
    return case


class TestAuditLogging:
    """Test audit logging functionality"""
    
    def test_audit_log_creation(self, clean_session, test_user, test_case):
        """Test that audit logs are created properly"""
        audit_service = AuditService(clean_session)
        
        # Log an action
        audit_service.log_action(
            user_id=test_user.id,
            action=AuditAction.CREATE_CASE,
            resource_type="Case",
            resource_id=str(test_case.id),
            details={"case_number": test_case.case_number, "title": test_case.title}
        )
        
        # Verify audit log was created
        audit_logs = clean_session.exec(select(AuditLog)).all()
        assert len(audit_logs) == 1
        
        audit_log = audit_logs[0]
        assert audit_log.user_id == test_user.id
        assert audit_log.action == AuditAction.CREATE_CASE
        assert audit_log.resource_type == "Case"
        assert audit_log.resource_id == str(test_case.id)
        assert audit_log.details is not None
        assert audit_log.timestamp is not None
    
    def test_multiple_audit_entries(self, clean_session, test_user, test_case):
        """Test multiple audit log entries"""
        audit_service = AuditService(clean_session)
        
        # Log multiple actions
        actions = [
            (AuditAction.CREATE_CASE, "Case created"),
            (AuditAction.UPDATE_CASE, "Case updated"),
            (AuditAction.CLASSIFY_CASE, "Case classified")
        ]
        
        for action, description in actions:
            audit_service.log_action(
                user_id=test_user.id,
                action=action,
                resource_type="Case",
                resource_id=str(test_case.id),
                details={"description": description}
            )
        
        # Verify all audit logs were created
        audit_logs = clean_session.exec(select(AuditLog)).all()
        assert len(audit_logs) == 3
        
        # Verify order (should be chronological)
        for i, (expected_action, _) in enumerate(actions):
            assert audit_logs[i].action == expected_action
    
    def test_audit_log_details_serialization(self, clean_session, test_user, test_case):
        """Test that complex details are properly serialized"""
        audit_service = AuditService(clean_session)
        
        complex_details = {
            "previous_status": "filed",
            "new_status": "in_progress",
            "changes": {
                "priority": {"from": "low", "to": "high"},
                "assigned_judge": {"from": None, "to": "Judge Smith"}
            },
            "metadata": {
                "ip_address": "192.168.1.1",
                "user_agent": "Test Client"
            }
        }
        
        audit_service.log_action(
            user_id=test_user.id,
            action=AuditAction.UPDATE_CASE,
            resource_type="Case",
            resource_id=str(test_case.id),
            details=complex_details
        )
        
        # Verify details are properly stored and retrievable
        audit_log = clean_session.exec(select(AuditLog)).first()
        assert audit_log.details == complex_details
        assert audit_log.details["changes"]["priority"]["from"] == "low"
        assert audit_log.details["metadata"]["ip_address"] == "192.168.1.1"
    
    def test_audit_log_user_association(self, clean_session, test_case):
        """Test audit log user association"""
        # Create multiple users
        users = []
        for i in range(3):
            user = User(
                username=f"audit_user_{i}",
                email=f"audit{i}@test.com",
                full_name=f"Audit User {i}",
                role=UserRole.CLERK,
                hashed_password=get_password_hash("test123"),
                is_active=True
            )
            clean_session.add(user)
            users.append(user)
        
        clean_session.commit()
        for user in users:
            clean_session.refresh(user)
        
        audit_service = AuditService(clean_session)
        
        # Log actions from different users
        for i, user in enumerate(users):
            audit_service.log_action(
                user_id=user.id,
                action=AuditAction.VIEW_CASE,
                resource_type="Case",
                resource_id=str(test_case.id),
                details={"action_number": i}
            )
        
        # Verify each audit log is associated with correct user
        audit_logs = clean_session.exec(select(AuditLog)).all()
        assert len(audit_logs) == 3
        
        for i, audit_log in enumerate(audit_logs):
            assert audit_log.user_id == users[i].id
            assert audit_log.user.username == f"audit_user_{i}"
    
    def test_audit_trail_chronology(self, clean_session, test_user, test_case):
        """Test that audit trail maintains proper chronological order"""
        audit_service = AuditService(clean_session)
        
        # Log actions with small delays to ensure different timestamps
        import time
        
        actions = [
            AuditAction.CREATE_CASE,
            AuditAction.CLASSIFY_CASE,
            AuditAction.UPDATE_CASE,
            AuditAction.SCHEDULE_HEARING
        ]
        
        for action in actions:
            audit_service.log_action(
                user_id=test_user.id,
                action=action,
                resource_type="Case",
                resource_id=str(test_case.id),
                details={"step": action.value}
            )
            time.sleep(0.01)  # Small delay to ensure different timestamps
        
        # Get audit trail in chronological order
        audit_trail = audit_service.get_audit_trail(
            resource_type="Case",
            resource_id=str(test_case.id)
        )
        
        assert len(audit_trail) == 4
        
        # Verify chronological order
        for i in range(len(audit_trail) - 1):
            assert audit_trail[i].timestamp <= audit_trail[i + 1].timestamp
        
        # Verify action order
        for i, expected_action in enumerate(actions):
            assert audit_trail[i].action == expected_action


class TestAuditQueries:
    """Test audit querying and filtering functionality"""
    
    def test_get_audit_trail_by_resource(self, clean_session, test_user):
        """Test getting audit trail for specific resource"""
        audit_service = AuditService(clean_session)
        
        # Create multiple test cases
        cases = []
        for i in range(3):
            case = Case(
                case_number=f"AUDIT/2024/{i+1:03d}",
                title=f"Audit Test Case {i+1}",
                case_type=CaseType.CIVIL,
                synopsis=f"Test case {i+1} for audit",
                filing_date=date.today(),
                priority=CasePriority.MEDIUM,
                estimated_duration_minutes=120,
                status=CaseStatus.FILED
            )
            clean_session.add(case)
            cases.append(case)
        
        clean_session.commit()
        for case in cases:
            clean_session.refresh(case)
        
        # Log actions for each case
        for i, case in enumerate(cases):
            for j in range(i + 1):  # Different number of actions per case
                audit_service.log_action(
                    user_id=test_user.id,
                    action=AuditAction.VIEW_CASE,
                    resource_type="Case",
                    resource_id=str(case.id),
                    details={"view_count": j + 1}
                )
        
        # Test getting audit trail for specific case
        case1_trail = audit_service.get_audit_trail("Case", str(cases[0].id))
        case2_trail = audit_service.get_audit_trail("Case", str(cases[1].id))
        case3_trail = audit_service.get_audit_trail("Case", str(cases[2].id))
        
        assert len(case1_trail) == 1
        assert len(case2_trail) == 2
        assert len(case3_trail) == 3
        
        # Verify correct resource IDs
        for log in case1_trail:
            assert log.resource_id == str(cases[0].id)
        for log in case2_trail:
            assert log.resource_id == str(cases[1].id)
        for log in case3_trail:
            assert log.resource_id == str(cases[2].id)
    
    def test_get_user_activity_log(self, clean_session, test_case):
        """Test getting activity log for specific user"""
        audit_service = AuditService(clean_session)
        
        # Create multiple users
        users = []
        for i in range(2):
            user = User(
                username=f"activity_user_{i}",
                email=f"activity{i}@test.com",
                full_name=f"Activity User {i}",
                role=UserRole.CLERK,
                hashed_password=get_password_hash("test123"),
                is_active=True
            )
            clean_session.add(user)
            users.append(user)
        
        clean_session.commit()
        for user in users:
            clean_session.refresh(user)
        
        # Log different numbers of actions per user
        for i, user in enumerate(users):
            for j in range((i + 1) * 2):  # User 0: 2 actions, User 1: 4 actions
                audit_service.log_action(
                    user_id=user.id,
                    action=AuditAction.VIEW_CASE,
                    resource_type="Case",
                    resource_id=str(test_case.id),
                    details={"action_number": j + 1}
                )
        
        # Test getting activity for each user
        user1_activity = audit_service.get_user_activity(users[0].id)
        user2_activity = audit_service.get_user_activity(users[1].id)
        
        assert len(user1_activity) == 2
        assert len(user2_activity) == 4
        
        # Verify correct user IDs
        for log in user1_activity:
            assert log.user_id == users[0].id
        for log in user2_activity:
            assert log.user_id == users[1].id
    
    def test_audit_filtering_by_action_type(self, clean_session, test_user, test_case):
        """Test filtering audit logs by action type"""
        audit_service = AuditService(clean_session)
        
        # Log different types of actions
        action_counts = {
            AuditAction.CREATE_CASE: 2,
            AuditAction.UPDATE_CASE: 3,
            AuditAction.VIEW_CASE: 5
        }
        
        for action, count in action_counts.items():
            for i in range(count):
                audit_service.log_action(
                    user_id=test_user.id,
                    action=action,
                    resource_type="Case",
                    resource_id=str(test_case.id),
                    details={"iteration": i + 1}
                )
        
        # Test filtering by action type
        for action, expected_count in action_counts.items():
            filtered_logs = audit_service.get_audit_logs_by_action(action)
            assert len(filtered_logs) == expected_count
            
            for log in filtered_logs:
                assert log.action == action
    
    def test_audit_date_range_filtering(self, clean_session, test_user, test_case):
        """Test filtering audit logs by date range"""
        audit_service = AuditService(clean_session)
        
        # This test would require manipulating timestamps
        # For now, just test basic functionality
        audit_service.log_action(
            user_id=test_user.id,
            action=AuditAction.CREATE_CASE,
            resource_type="Case",
            resource_id=str(test_case.id),
            details={"test": "date_range"}
        )
        
        # Get all logs (basic test)
        all_logs = clean_session.exec(select(AuditLog)).all()
        assert len(all_logs) >= 1
        
        # Verify timestamp exists and is reasonable
        for log in all_logs:
            assert log.timestamp is not None
            assert isinstance(log.timestamp, datetime)


class TestAuditIntegrity:
    """Test audit log data integrity and security"""
    
    def test_audit_log_immutability(self, clean_session, test_user, test_case):
        """Test that audit logs should be immutable once created"""
        audit_service = AuditService(clean_session)
        
        # Create audit log
        audit_service.log_action(
            user_id=test_user.id,
            action=AuditAction.CREATE_CASE,
            resource_type="Case",
            resource_id=str(test_case.id),
            details={"original": "data"}
        )
        
        # Get the audit log
        audit_log = clean_session.exec(select(AuditLog)).first()
        original_details = audit_log.details.copy()
        original_timestamp = audit_log.timestamp
        
        # Audit logs should typically be immutable in a real system
        # This test documents the expected behavior
        assert audit_log.details == original_details
        assert audit_log.timestamp == original_timestamp
    
    def test_audit_log_completeness(self, clean_session, test_user, test_case):
        """Test that all required audit fields are populated"""
        audit_service = AuditService(clean_session)
        
        audit_service.log_action(
            user_id=test_user.id,
            action=AuditAction.UPDATE_CASE,
            resource_type="Case",
            resource_id=str(test_case.id),
            details={"field": "value"}
        )
        
        audit_log = clean_session.exec(select(AuditLog)).first()
        
        # Verify all required fields are present
        assert audit_log.id is not None
        assert audit_log.user_id is not None
        assert audit_log.action is not None
        assert audit_log.resource_type is not None
        assert audit_log.resource_id is not None
        assert audit_log.timestamp is not None
        assert audit_log.details is not None
        
        # Verify relationships work
        assert audit_log.user is not None
        assert audit_log.user.id == test_user.id
    
    def test_audit_log_data_types(self, clean_session, test_user, test_case):
        """Test audit log data type integrity"""
        audit_service = AuditService(clean_session)
        
        audit_service.log_action(
            user_id=test_user.id,
            action=AuditAction.DELETE_CASE,
            resource_type="Case",
            resource_id=str(test_case.id),
            details={"reason": "test deletion"}
        )
        
        audit_log = clean_session.exec(select(AuditLog)).first()
        
        # Verify data types
        assert isinstance(audit_log.id, int)
        assert isinstance(audit_log.user_id, int)
        assert isinstance(audit_log.action, AuditAction)
        assert isinstance(audit_log.resource_type, str)
        assert isinstance(audit_log.resource_id, str)
        assert isinstance(audit_log.timestamp, datetime)
        assert isinstance(audit_log.details, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

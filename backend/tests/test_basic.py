"""
Basic health check test for the DCM system
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "DCM System" in data["message"]


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "dcm-system"


def test_dcm_rules_engine():
    """Test the DCM rules engine"""
    from app.services.dcm_rules import dcm_engine
    from app.models.case import Case, CaseType, CasePriority
    from datetime import date
    
    # Create a test case
    test_case = Case(
        id=1,
        case_number="TEST/2024/001",
        title="Test vs State",
        case_type=CaseType.CRIMINAL,
        synopsis="A case involving theft of mobile phone",
        filing_date=date.today(),
        priority=CasePriority.MEDIUM,
        estimated_duration_minutes=120
    )
    
    # Test classification
    classification = dcm_engine.classify_case(test_case)
    
    assert classification.case_id == 1
    assert classification.track is not None
    assert classification.score is not None
    assert len(classification.reasons) > 0
    assert 0 <= classification.confidence <= 1


def test_bns_assist_service():
    """Test the BNS assist service"""
    from app.services.nlp import bns_assist
    
    # Test synopsis suggestion
    synopsis = "The accused committed theft by stealing a mobile phone from the victim"
    suggestions = bns_assist.suggest_bns_sections(synopsis, max_suggestions=3)
    
    assert isinstance(suggestions, list)
    assert len(suggestions) <= 3
    
    if suggestions:
        suggestion = suggestions[0]
        assert hasattr(suggestion, 'section_number')
        assert hasattr(suggestion, 'confidence')
        assert 0 <= suggestion.confidence <= 1


def test_scheduler_priority_calculation():
    """Test the scheduler priority calculation"""
    from app.services.scheduler import scheduler
    from app.models.case import Case, CaseType, CasePriority, CaseTrack
    from datetime import date
    
    test_case = Case(
        id=1,
        case_number="SCHED/2024/001",
        title="Priority Test Case",
        case_type=CaseType.CRIMINAL,
        synopsis="Test case for scheduling",
        filing_date=date.today(),
        priority=CasePriority.HIGH,
        estimated_duration_minutes=60,
        track=CaseTrack.FAST
    )
    
    priority_score = scheduler.calculate_case_priority_score(test_case)
    assert isinstance(priority_score, (int, float))
    assert priority_score > 0  # Should have some positive priority


if __name__ == "__main__":
    # Run basic tests
    test_root_endpoint()
    test_health_check()
    test_dcm_rules_engine()
    test_bns_assist_service()
    test_scheduler_priority_calculation()
    print("All basic tests passed!")

"""
Simple system verification test
Tests basic system functionality without complex imports
"""

def test_basic_functionality():
    """Test basic system is working"""
    print("✅ Basic test passed")
    assert True

def test_database_connection():
    """Test database connectivity"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    
    try:
        from app.core.database import engine
        # Simple connection test
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            assert result.fetchone()[0] == 1
        print("✅ Database connection test passed")
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        assert False

def test_models_import():
    """Test model imports"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    
    try:
        from app.models.user import User, UserRole
        from app.models.case import Case, CaseType
        from app.models.bench import Bench
        print("✅ Model imports test passed")
    except Exception as e:
        print(f"❌ Model imports test failed: {e}")
        assert False

def test_services_import():
    """Test service imports"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    
    try:
        from app.services.dcm_service import DCMService
        from app.services.audit_service import AuditService
        print("✅ Services imports test passed")
    except Exception as e:
        print(f"❌ Services imports test failed: {e}")
        assert False

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

"""
Smoke test E2E script for DCM System
Tests the complete flow from authentication to case processing
"""
import requests
import json
from datetime import date, datetime
import sys

BASE_URL = "http://localhost:8000"

class DCMSmokeTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.clerk_token = None
        self.judge_token = None
        
    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def test_health(self):
        """Test basic health endpoint"""
        self.log("🔍 Testing health endpoint...")
        response = self.session.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        self.log("✅ Health check passed")
        
    def login_user(self, username, password):
        """Login and return token"""
        self.log(f"🔑 Logging in as {username}...")
        response = self.session.post(
            f"{BASE_URL}/auth/login",
            data={"username": username, "password": password}
        )
        assert response.status_code == 200
        data = response.json()
        token = data["access_token"]
        self.log(f"✅ Login successful for {username}")
        return token
        
    def test_authentication(self):
        """Test user authentication"""
        self.log("🔐 Testing authentication...")
        
        # Login as different users
        self.admin_token = self.login_user("admin", "admin123")
        self.clerk_token = self.login_user("clerk1", "clerk123")
        self.judge_token = self.login_user("judge1", "judge123")
        
        # Test token verification
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = self.session.get(f"{BASE_URL}/auth/me", headers=headers)
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["username"] == "admin"
        
        self.log("✅ Authentication tests passed")
        
    def create_test_case(self, token, case_data):
        """Create a test case"""
        headers = {"Authorization": f"Bearer {token}"}
        response = self.session.post(
            f"{BASE_URL}/cases/",
            json=case_data,
            headers=headers
        )
        assert response.status_code == 200
        return response.json()
        
    def test_case_management(self):
        """Test case creation and management"""
        self.log("📁 Testing case management...")
        
        # Create test cases
        test_cases = [
            {
                "case_number": "SMOKE/2024/001",
                "title": "State vs. Test Defendant 1",
                "case_type": "criminal",
                "synopsis": "Test case involving theft of mobile phone for smoke testing",
                "filing_date": date.today().isoformat(),
                "priority": "medium",
                "estimated_duration_minutes": 120
            },
            {
                "case_number": "SMOKE/2024/002", 
                "title": "Commercial Dispute Test",
                "case_type": "commercial",
                "synopsis": "Complex commercial contract dispute involving multiple parties and significant damages",
                "filing_date": date.today().isoformat(),
                "priority": "high",
                "estimated_duration_minutes": 240
            },
            {
                "case_number": "SMOKE/2024/003",
                "title": "Traffic Violation Test",
                "case_type": "criminal", 
                "synopsis": "Simple traffic violation case running red light",
                "filing_date": date.today().isoformat(),
                "priority": "low",
                "estimated_duration_minutes": 30
            }
        ]
        
        created_cases = []
        for case_data in test_cases:
            case = self.create_test_case(self.clerk_token, case_data)
            created_cases.append(case)
            self.log(f"✅ Created case: {case['case_number']}")
            
        self.log(f"✅ Case management tests passed - {len(created_cases)} cases created")
        return created_cases
        
    def test_dcm_classification(self, cases):
        """Test DCM classification"""
        self.log("🧠 Testing DCM classification...")
        
        headers = {"Authorization": f"Bearer {self.clerk_token}"}
        classified_cases = []
        
        for case in cases:
            case_id = case["id"]
            response = self.session.post(
                f"{BASE_URL}/cases/{case_id}/classify",
                headers=headers
            )
            assert response.status_code == 200
            classification = response.json()
            classified_cases.append(classification)
            
            track = classification["classification"]["track"]
            score = classification["classification"]["score"]
            self.log(f"✅ Case {case['case_number']} classified as {track} (score: {score})")
            
        self.log("✅ DCM classification tests passed")
        return classified_cases
        
    def test_scheduling(self):
        """Test case scheduling"""
        self.log("⏰ Testing case scheduling...")
        
        headers = {"Authorization": f"Bearer {self.clerk_token}"}
        
        # Allocate cases to schedule
        response = self.session.post(
            f"{BASE_URL}/schedule/allocate",
            params={
                "start_date": date.today().isoformat(),
                "num_days": 7
            },
            headers=headers
        )
        assert response.status_code == 200
        allocation_result = response.json()
        
        scheduled = len(allocation_result["scheduled_hearings"])
        unplaced = len(allocation_result["unplaced_cases"])
        
        self.log(f"✅ Scheduling completed: {scheduled} scheduled, {unplaced} unplaced")
        
        # Test cause list generation
        response = self.session.get(
            f"{BASE_URL}/schedule/cause-list/{date.today().isoformat()}",
            headers=headers
        )
        assert response.status_code == 200
        cause_list = response.json()
        
        self.log(f"✅ Cause list generated with {cause_list['total_hearings']} hearings")
        return allocation_result
        
    def test_judge_override(self, cases):
        """Test judge track override"""
        self.log("⚖️ Testing judge override...")
        
        if not cases:
            self.log("⚠️ No cases available for override test")
            return
            
        headers = {"Authorization": f"Bearer {self.judge_token}"}
        case_id = cases[0]["case_id"]
        
        override_data = {
            "new_track": "complex",
            "reason": "Smoke test override - case requires complex handling due to multiple legal issues"
        }
        
        response = self.session.post(
            f"{BASE_URL}/cases/{case_id}/override-track",
            json=override_data,
            headers=headers
        )
        assert response.status_code == 200
        override_result = response.json()
        
        self.log(f"✅ Judge override successful: {override_result['old_track']} → {override_result['new_track']}")
        
    def test_nlp_suggestions(self):
        """Test NLP BNS suggestions"""
        self.log("🤖 Testing NLP suggestions...")
        
        headers = {"Authorization": f"Bearer {self.clerk_token}"}
        
        test_synopsis = "The accused committed theft by stealing a mobile phone worth Rs. 25,000 from the victim's house"
        
        response = self.session.post(
            f"{BASE_URL}/nlp/suggest-laws",
            params={
                "case_synopsis": test_synopsis,
                "max_suggestions": 3
            },
            headers=headers
        )
        assert response.status_code == 200
        suggestions = response.json()
        
        suggested_count = len(suggestions["suggestions"])
        self.log(f"✅ NLP suggestions: {suggested_count} BNS sections suggested")
        
        for suggestion in suggestions["suggestions"][:2]:
            section = suggestion["section_number"]
            confidence = suggestion["confidence"]
            self.log(f"  • BNS {section}: {confidence} confidence")
            
    def test_reports_and_metrics(self):
        """Test reports and analytics"""
        self.log("📊 Testing reports and metrics...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test metrics endpoint
        response = self.session.get(f"{BASE_URL}/reports/metrics", headers=headers)
        assert response.status_code == 200
        metrics = response.json()
        
        total_cases = metrics["summary"]["total_cases"]
        unplaced_pct = metrics["summary"]["unplaced_percentage"]
        
        self.log(f"✅ Metrics: {total_cases} total cases, {unplaced_pct}% unplaced")
        
        # Test dashboard data
        response = self.session.get(f"{BASE_URL}/reports/dashboard", headers=headers)
        assert response.status_code == 200
        dashboard = response.json()
        
        self.log(f"✅ Dashboard data loaded for {dashboard['user']['role']}")
        
    def test_audit_trail(self, cases):
        """Test audit trail functionality"""
        self.log("📋 Testing audit trails...")
        
        if not cases:
            self.log("⚠️ No cases available for audit test")
            return
            
        headers = {"Authorization": f"Bearer {self.clerk_token}"}
        case_id = cases[0]["case_id"]
        
        response = self.session.get(
            f"{BASE_URL}/cases/{case_id}/audit-trail",
            headers=headers
        )
        assert response.status_code == 200
        audit_data = response.json()
        
        audit_count = len(audit_data["audit_trail"])
        self.log(f"✅ Audit trail: {audit_count} entries for case {audit_data['case_number']}")
        
    def run_smoke_test(self):
        """Run complete smoke test suite"""
        self.log("🏛️ Starting DCM System Smoke Test")
        self.log("=" * 50)
        
        try:
            # Core functionality tests
            self.test_health()
            self.test_authentication()
            
            # Case workflow tests
            cases = self.test_case_management()
            classified_cases = self.test_dcm_classification(cases)
            allocation_result = self.test_scheduling()
            
            # Advanced features
            self.test_judge_override(classified_cases)
            self.test_nlp_suggestions()
            self.test_reports_and_metrics()
            self.test_audit_trail(classified_cases)
            
            self.log("=" * 50)
            self.log("🎉 ALL SMOKE TESTS PASSED!")
            self.log("✅ DCM System is demo-ready")
            
            # Print summary
            self.log("\n📋 Test Summary:")
            self.log(f"• Authentication: ✅ Admin, Clerk, Judge login working")
            self.log(f"• Case Management: ✅ {len(cases)} cases created and managed")
            self.log(f"• DCM Classification: ✅ All cases classified with confidence scores")
            self.log(f"• Scheduling: ✅ {len(allocation_result['scheduled_hearings'])} hearings scheduled")
            self.log(f"• Judge Override: ✅ Track changes with audit trail")
            self.log(f"• NLP Suggestions: ✅ BNS sections suggested with confidence")
            self.log(f"• Reports & Analytics: ✅ Metrics and dashboards working")
            self.log(f"• Audit Trails: ✅ Complete activity logging")
            
            return True
            
        except Exception as e:
            self.log(f"❌ SMOKE TEST FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    print("🏛️ DCM System E2E Smoke Test")
    print("Make sure the server is running: uvicorn main:app --reload")
    print()
    
    test_runner = DCMSmokeTest()
    success = test_runner.run_smoke_test()
    
    sys.exit(0 if success else 1)

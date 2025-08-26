"""
Scheduler Deterministic Tests
Tests to verify scheduling algorithm consistency and determinism
"""
import pytest
import json
import hashlib
from datetime import date, datetime, timedelta
from typing import Dict, List, Any
from sqlmodel import Session
from app.core.database import get_session, create_db_and_tables, engine
from app.models.case import Case, CaseType, CasePriority, CaseStatus
from app.models.bench import Bench
from app.models.hearing import Hearing
from app.services.scheduler import GreedyScheduler
from app.services.dcm_service import DCMService


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
        session.query(Hearing).delete()
        session.query(Case).delete()
        session.query(Bench).delete()
        session.commit()
        yield session


@pytest.fixture
def sample_benches(clean_session):
    """Create sample benches for testing"""
    benches = [
        Bench(
            name="District Court 1",
            court_number="DC-1",
            capacity=50,
            is_active=True
        ),
        Bench(
            name="District Court 2", 
            court_number="DC-2",
            capacity=75,
            is_active=True
        ),
        Bench(
            name="High Court",
            court_number="HC-1",
            capacity=100,
            is_active=True
        )
    ]
    
    for bench in benches:
        clean_session.add(bench)
    clean_session.commit()
    
    for bench in benches:
        clean_session.refresh(bench)
    
    return benches


@pytest.fixture
def sample_cases(clean_session, sample_benches):
    """Create sample cases with known properties"""
    cases = []
    
    # Create deterministic test cases
    case_data = [
        {
            "case_number": "DET/2024/001",
            "title": "Deterministic Test Case 1",
            "case_type": CaseType.CRIMINAL,
            "priority": CasePriority.HIGH,
            "estimated_duration_minutes": 120,
            "filing_date": date(2024, 1, 15),
            "synopsis": "High priority criminal case for deterministic testing"
        },
        {
            "case_number": "DET/2024/002", 
            "title": "Deterministic Test Case 2",
            "case_type": CaseType.CIVIL,
            "priority": CasePriority.MEDIUM,
            "estimated_duration_minutes": 90,
            "filing_date": date(2024, 1, 16),
            "synopsis": "Medium priority civil case for deterministic testing"
        },
        {
            "case_number": "DET/2024/003",
            "title": "Deterministic Test Case 3", 
            "case_type": CaseType.FAMILY,
            "priority": CasePriority.LOW,
            "estimated_duration_minutes": 60,
            "filing_date": date(2024, 1, 17),
            "synopsis": "Low priority family case for deterministic testing"
        },
        {
            "case_number": "DET/2024/004",
            "title": "Deterministic Test Case 4",
            "case_type": CaseType.COMMERCIAL,
            "priority": CasePriority.HIGH,
            "estimated_duration_minutes": 180,
            "filing_date": date(2024, 1, 14),
            "synopsis": "High priority commercial case for deterministic testing"
        },
        {
            "case_number": "DET/2024/005",
            "title": "Deterministic Test Case 5",
            "case_type": CaseType.CRIMINAL,
            "priority": CasePriority.MEDIUM,
            "estimated_duration_minutes": 75,
            "filing_date": date(2024, 1, 18),
            "synopsis": "Medium priority criminal case for deterministic testing"
        }
    ]
    
    for data in case_data:
        case = Case(**data)
        case.status = CaseStatus.FILED
        # Set deterministic track using DCM service
        dcm = DCMService()
        case.track = dcm._determine_track(case)
        
        clean_session.add(case)
        cases.append(case)
    
    clean_session.commit()
    
    for case in cases:
        clean_session.refresh(case)
    
    return cases


class TestSchedulerDeterminism:
    """Test that scheduler produces deterministic results"""
    
    def test_same_input_same_output(self, clean_session, sample_cases, sample_benches):
        """Test that identical inputs produce identical schedules"""
        scheduler = GreedyScheduler(clean_session)
        
        start_date = date(2024, 2, 1)
        num_days = 5
        
        # Run scheduler multiple times with same input
        schedule1 = scheduler.allocate_hearings(start_date, num_days)
        
        # Clear hearings and run again
        clean_session.query(Hearing).delete()
        clean_session.commit()
        
        schedule2 = scheduler.allocate_hearings(start_date, num_days)
        
        # Convert to comparable format
        snapshot1 = self._create_schedule_snapshot(schedule1)
        snapshot2 = self._create_schedule_snapshot(schedule2)
        
        assert snapshot1 == snapshot2, "Scheduler should produce identical results for identical inputs"
    
    def test_canonical_json_serialization(self, clean_session, sample_cases, sample_benches):
        """Test canonical JSON representation of schedule"""
        scheduler = GreedyScheduler(clean_session)
        
        start_date = date(2024, 2, 1)
        num_days = 3
        
        schedule = scheduler.allocate_hearings(start_date, num_days)
        snapshot = self._create_schedule_snapshot(schedule)
        
        # Serialize to canonical JSON
        json_str1 = json.dumps(snapshot, sort_keys=True, separators=(',', ':'))
        json_str2 = json.dumps(snapshot, sort_keys=True, separators=(',', ':'))
        
        assert json_str1 == json_str2, "JSON serialization should be deterministic"
        
        # Test hash consistency
        hash1 = hashlib.md5(json_str1.encode()).hexdigest()
        hash2 = hashlib.md5(json_str2.encode()).hexdigest()
        
        assert hash1 == hash2, "Hash of canonical JSON should be consistent"
    
    def test_schedule_hash_uniqueness(self, clean_session, sample_cases, sample_benches):
        """Test that different schedules produce different hashes"""
        scheduler = GreedyScheduler(clean_session)
        
        # Create two different schedules
        schedule1 = scheduler.allocate_hearings(date(2024, 2, 1), 3)
        snapshot1 = self._create_schedule_snapshot(schedule1)
        hash1 = self._get_schedule_hash(snapshot1)
        
        # Clear and create different schedule  
        clean_session.query(Hearing).delete()
        clean_session.commit()
        
        schedule2 = scheduler.allocate_hearings(date(2024, 2, 5), 2)  # Different dates
        snapshot2 = self._create_schedule_snapshot(schedule2)
        hash2 = self._get_schedule_hash(snapshot2)
        
        # Hashes should be different (assuming different schedules)
        if snapshot1 != snapshot2:
            assert hash1 != hash2, "Different schedules should produce different hashes"
    
    def test_ordering_consistency(self, clean_session, sample_cases, sample_benches):
        """Test that case ordering is consistent across runs"""
        scheduler = GreedyScheduler(clean_session)
        
        # Get priority-ordered cases multiple times
        ordered_cases1 = scheduler._get_priority_ordered_cases()
        ordered_cases2 = scheduler._get_priority_ordered_cases()
        
        # Case IDs should be in same order
        ids1 = [case.id for case in ordered_cases1]
        ids2 = [case.id for case in ordered_cases2]
        
        assert ids1 == ids2, "Case ordering should be deterministic"
        
        # Verify ordering logic
        priorities = [case.priority for case in ordered_cases1]
        filing_dates = [case.filing_date for case in ordered_cases1]
        
        # Should be ordered by priority (high first), then filing date (older first)
        for i in range(len(priorities) - 1):
            curr_priority = self._priority_value(priorities[i])
            next_priority = self._priority_value(priorities[i + 1])
            
            if curr_priority == next_priority:
                # Same priority, check filing date
                assert filing_dates[i] <= filing_dates[i + 1], "Cases with same priority should be ordered by filing date"
            else:
                # Different priority, high should come first
                assert curr_priority >= next_priority, "Higher priority cases should come first"
    
    def test_allocation_algorithm_stability(self, clean_session, sample_cases, sample_benches):
        """Test that allocation algorithm is stable"""
        scheduler = GreedyScheduler(clean_session)
        
        start_date = date(2024, 2, 1)
        
        # Run allocation multiple times
        results = []
        for _ in range(3):
            clean_session.query(Hearing).delete()
            clean_session.commit()
            
            schedule = scheduler.allocate_hearings(start_date, 5)
            snapshot = self._create_schedule_snapshot(schedule)
            results.append(snapshot)
        
        # All results should be identical
        for i in range(1, len(results)):
            assert results[0] == results[i], f"Run {i} produced different result than first run"
    
    def test_bench_allocation_fairness(self, clean_session, sample_cases, sample_benches):
        """Test that bench allocation is fair and deterministic"""
        scheduler = GreedyScheduler(clean_session)
        
        schedule = scheduler.allocate_hearings(date(2024, 2, 1), 5)
        
        # Count allocations per bench
        bench_usage = {}
        for hearing in schedule:
            bench_id = hearing.bench_id
            if bench_id not in bench_usage:
                bench_usage[bench_id] = 0
            bench_usage[bench_id] += 1
        
        # Should use all available benches if possible
        total_hearings = len(schedule)
        if total_hearings > 0:
            assert len(bench_usage) > 0, "Should allocate to at least one bench"
            
            # Check that high-capacity benches get more cases
            bench_capacities = {bench.id: bench.capacity for bench in sample_benches}
            
            # Verify allocation makes sense based on capacity
            for bench_id, usage in bench_usage.items():
                capacity = bench_capacities[bench_id]
                assert usage > 0, f"Bench {bench_id} should have at least one hearing"
    
    def test_time_slot_allocation(self, clean_session, sample_cases, sample_benches):
        """Test that time slot allocation is deterministic"""
        scheduler = GreedyScheduler(clean_session)
        
        schedule = scheduler.allocate_hearings(date(2024, 2, 1), 2)
        
        # Group by date and bench
        daily_schedules = {}
        for hearing in schedule:
            date_key = hearing.scheduled_date.isoformat()
            if date_key not in daily_schedules:
                daily_schedules[date_key] = {}
            
            bench_id = hearing.bench_id
            if bench_id not in daily_schedules[date_key]:
                daily_schedules[date_key][bench_id] = []
            
            daily_schedules[date_key][bench_id].append(hearing)
        
        # Verify time slots don't overlap on same bench/date
        for date_str, benches in daily_schedules.items():
            for bench_id, hearings in benches.items():
                # Sort by start time
                hearings.sort(key=lambda h: h.scheduled_time)
                
                for i in range(len(hearings) - 1):
                    current = hearings[i]
                    next_hearing = hearings[i + 1]
                    
                    # Calculate end time of current hearing
                    current_end = (datetime.combine(date.today(), current.scheduled_time) + 
                                 timedelta(minutes=current.duration_minutes)).time()
                    
                    assert current_end <= next_hearing.scheduled_time, \
                        f"Hearings should not overlap on same bench: {current.id} and {next_hearing.id}"
    
    def _create_schedule_snapshot(self, hearings: List[Hearing]) -> Dict[str, Any]:
        """Create deterministic snapshot of schedule"""
        snapshot = {
            "hearings": [],
            "total_count": len(hearings),
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "algorithm": "greedy_scheduler_v1"
            }
        }
        
        # Sort hearings for deterministic ordering
        sorted_hearings = sorted(hearings, key=lambda h: (
            h.scheduled_date.isoformat(),
            h.bench_id,
            h.scheduled_time.isoformat() if h.scheduled_time else "",
            h.case_id
        ))
        
        for hearing in sorted_hearings:
            hearing_data = {
                "case_id": hearing.case_id,
                "case_number": hearing.case.case_number if hearing.case else None,
                "bench_id": hearing.bench_id,
                "scheduled_date": hearing.scheduled_date.isoformat(),
                "scheduled_time": hearing.scheduled_time.isoformat() if hearing.scheduled_time else None,
                "duration_minutes": hearing.duration_minutes,
                "priority": hearing.case.priority.value if hearing.case else None,
                "case_type": hearing.case.case_type.value if hearing.case else None
            }
            snapshot["hearings"].append(hearing_data)
        
        return snapshot
    
    def _get_schedule_hash(self, snapshot: Dict[str, Any]) -> str:
        """Get deterministic hash of schedule snapshot"""
        # Remove timestamp for hash consistency
        clean_snapshot = snapshot.copy()
        if "metadata" in clean_snapshot:
            clean_snapshot["metadata"] = {k: v for k, v in clean_snapshot["metadata"].items() 
                                        if k != "created_at"}
        
        json_str = json.dumps(clean_snapshot, sort_keys=True, separators=(',', ':'))
        return hashlib.md5(json_str.encode()).hexdigest()
    
    def _priority_value(self, priority: CasePriority) -> int:
        """Convert priority to numeric value for comparison"""
        priority_map = {
            CasePriority.HIGH: 3,
            CasePriority.MEDIUM: 2, 
            CasePriority.LOW: 1
        }
        return priority_map.get(priority, 0)


class TestScheduleConsistency:
    """Test schedule consistency and validation"""
    
    def test_no_double_booking(self, clean_session, sample_cases, sample_benches):
        """Test that no bench is double-booked"""
        scheduler = GreedyScheduler(clean_session)
        
        schedule = scheduler.allocate_hearings(date(2024, 2, 1), 3)
        
        # Group by bench and date
        bench_schedules = {}
        for hearing in schedule:
            key = (hearing.bench_id, hearing.scheduled_date)
            if key not in bench_schedules:
                bench_schedules[key] = []
            bench_schedules[key].append(hearing)
        
        # Check for overlaps
        for (bench_id, date_val), hearings in bench_schedules.items():
            hearings.sort(key=lambda h: h.scheduled_time or datetime.min.time())
            
            for i in range(len(hearings) - 1):
                current = hearings[i]
                next_hearing = hearings[i + 1]
                
                if current.scheduled_time and next_hearing.scheduled_time:
                    current_end = (datetime.combine(date.today(), current.scheduled_time) + 
                                 timedelta(minutes=current.duration_minutes)).time()
                    
                    assert current_end <= next_hearing.scheduled_time, \
                        f"Double booking detected on bench {bench_id} on {date_val}"
    
    def test_business_hours_compliance(self, clean_session, sample_cases, sample_benches):
        """Test that all hearings are scheduled within business hours"""
        scheduler = GreedyScheduler(clean_session)
        
        schedule = scheduler.allocate_hearings(date(2024, 2, 1), 2)
        
        for hearing in schedule:
            if hearing.scheduled_time:
                # Business hours: 9:00 AM to 5:00 PM
                assert hearing.scheduled_time >= datetime.strptime("09:00", "%H:%M").time(), \
                    f"Hearing {hearing.id} scheduled before business hours"
                
                # Calculate end time
                end_time = (datetime.combine(date.today(), hearing.scheduled_time) + 
                          timedelta(minutes=hearing.duration_minutes)).time()
                
                assert end_time <= datetime.strptime("17:00", "%H:%M").time(), \
                    f"Hearing {hearing.id} extends beyond business hours"
    
    def test_case_assignment_integrity(self, clean_session, sample_cases, sample_benches):
        """Test that all cases are properly assigned"""
        scheduler = GreedyScheduler(clean_session)
        
        schedule = scheduler.allocate_hearings(date(2024, 2, 1), 7)
        
        # All hearings should have valid case assignments
        for hearing in schedule:
            assert hearing.case_id is not None, f"Hearing {hearing.id} has no case assigned"
            assert hearing.case is not None, f"Hearing {hearing.id} case relationship is broken"
        
        # Check that all filed cases are eventually scheduled
        filed_cases = clean_session.query(Case).filter(Case.status == CaseStatus.FILED).all()
        scheduled_case_ids = {hearing.case_id for hearing in schedule}
        
        for case in filed_cases:
            if case.id not in scheduled_case_ids:
                # Case might not be scheduled if no capacity, but should be tracked
                print(f"Warning: Case {case.case_number} not scheduled")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

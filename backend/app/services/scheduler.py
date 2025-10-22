"""
Case Scheduling Service using Greedy Allocation Algorithm
Allocates cases to daily cause lists with 15% slack
"""
import heapq
from datetime import date, time, timedelta
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import settings
from app.models.bench import Bench
from app.models.case import Case, CaseTrack
from app.models.hearing import Hearing, HearingCreate, HearingStatus
from app.models.user import User, UserRole


class SchedulingResult:
    """Result of scheduling operation"""
    def __init__(self):
        self.scheduled_hearings: List[HearingCreate] = []
        self.unplaced_cases: List[Case] = []
        self.scheduling_stats: Dict[str, Any] = {}


class CaseScheduler:
    """Greedy allocation scheduler for case hearings"""

    def __init__(self):
        self.daily_slots = settings.DAILY_HEARING_SLOTS
        self.slack_percentage = settings.SLACK_PERCENTAGE
        self.effective_slots = int(self.daily_slots * (1 - self.slack_percentage))

        # Track prioritization weights
        self.track_weights = {
            CaseTrack.FAST: 3,     # High priority
            CaseTrack.REGULAR: 2,  # Medium priority
            CaseTrack.COMPLEX: 1   # Lower priority (longer cases)
        }

    def calculate_case_priority_score(self, case: Case) -> float:
        """
        Calculate priority score for case scheduling
        Higher score = higher priority
        """
        score = 0.0

        # Track-based priority
        track_weight = self.track_weights.get(case.track, 1)
        score += track_weight * 10

        # Age of case (older cases get higher priority)
        days_old = (date.today() - case.filing_date).days
        score += min(days_old * 0.1, 10)  # Cap at 10 points for age

        # Priority level
        priority_scores = {
            "urgent": 20,
            "high": 15,
            "medium": 10,
            "low": 5
        }
        score += priority_scores.get(case.priority.value, 10)

        # Penalty for estimated duration (longer cases get lower priority in greedy)
        duration_penalty = case.estimated_duration_minutes / 60  # Convert to hours
        score -= duration_penalty * 2

        return score

    def get_available_slots_for_date(
        self,
        target_date: date,
        existing_hearings: List[Hearing],
        benches: List[Bench]
    ) -> Dict[int, int]:
        """
        Get available slots per bench for a given date

        Returns:
            Dict mapping bench_id to available_minutes
        """
        # Initialize with full capacity (8 hours = 480 minutes per bench)
        bench_capacity = {bench.id: 480 for bench in benches if bench.is_active}

        # Subtract already scheduled hearings
        for hearing in existing_hearings:
            if hearing.hearing_date == target_date and hearing.bench_id in bench_capacity:
                bench_capacity[hearing.bench_id] -= hearing.estimated_duration_minutes

        # Apply slack (reserve some capacity)
        for bench_id in bench_capacity:
            bench_capacity[bench_id] = int(bench_capacity[bench_id] * (1 - self.slack_percentage))
            # Ensure non-negative
            bench_capacity[bench_id] = max(0, bench_capacity[bench_id])

        return bench_capacity

    def find_best_bench_and_time(
        self,
        case: Case,
        target_date: date,
        available_slots: Dict[int, int],
        judges: List[User]
    ) -> Optional[Tuple[int, int, time]]:
        """
        Find the best bench, judge, and time slot for a case

        Returns:
            Tuple of (bench_id, judge_id, start_time) or None if no slot available
        """
        required_duration = case.estimated_duration_minutes

        # Find benches with sufficient capacity
        suitable_benches = [
            (bench_id, available_minutes)
            for bench_id, available_minutes in available_slots.items()
            if available_minutes >= required_duration
        ]

        if not suitable_benches:
            return None

        # Sort by available capacity (use bench with least excess capacity first)
        suitable_benches.sort(key=lambda x: x[1])

        # Get available judges (only judges and admins can preside)
        available_judges = [
            judge for judge in judges
            if judge.role in [UserRole.JUDGE, UserRole.ADMIN] and judge.is_active
        ]

        if not available_judges:
            return None

        # For simplicity, assign first available judge
        # In a real system, you'd check judge availability and preferences
        selected_judge = available_judges[0]
        selected_bench = suitable_benches[0][0]

        # Calculate start time (simplified - start at 9 AM for now)
        start_time = time(9, 0)  # 9:00 AM

        return (selected_bench, selected_judge.id, start_time)

    def schedule_cases(
        self,
        cases: List[Case],
        start_date: date,
        num_days: int,
        benches: List[Bench],
        judges: List[User],
        existing_hearings: List[Hearing]
    ) -> SchedulingResult:
        """
        Schedule cases using greedy allocation algorithm

        Args:
            cases: List of cases to schedule
            start_date: Start date for scheduling
            num_days: Number of days to schedule over
            benches: Available benches
            judges: Available judges
            existing_hearings: Already scheduled hearings

        Returns:
            SchedulingResult with scheduled hearings and unplaced cases
        """
        result = SchedulingResult()

        # Filter cases that need scheduling (not already scheduled)
        scheduled_case_ids = {h.case_id for h in existing_hearings}
        unscheduled_cases = [case for case in cases if case.id not in scheduled_case_ids]

        # Sort cases by priority score (highest first)
        case_priority_heap = []
        for case in unscheduled_cases:
            priority_score = self.calculate_case_priority_score(case)
            # Use negative score for max heap behavior
            heapq.heappush(case_priority_heap, (-priority_score, case.id, case))

        # Track scheduling statistics
        stats = {
            "total_cases": len(unscheduled_cases),
            "scheduled_count": 0,
            "unplaced_count": 0,
            "total_duration_scheduled": 0,
            "scheduling_dates": []
        }

        # Schedule over the specified date range
        for day_offset in range(num_days):
            current_date = start_date + timedelta(days=day_offset)

            # Get available slots for this date
            date_hearings = [h for h in existing_hearings if h.hearing_date == current_date]
            available_slots = self.get_available_slots_for_date(
                current_date, date_hearings, benches
            )

            daily_scheduled = 0
            daily_duration = 0

            # Process cases in priority order
            temp_heap = []
            while case_priority_heap:
                neg_priority, case_id, case = heapq.heappop(case_priority_heap)

                # Try to schedule this case
                bench_assignment = self.find_best_bench_and_time(
                    case, current_date, available_slots, judges
                )

                if bench_assignment:
                    bench_id, judge_id, start_time = bench_assignment

                    # Create hearing
                    hearing = HearingCreate(
                        case_id=case.id,
                        judge_id=judge_id,
                        bench_id=bench_id,
                        hearing_date=current_date,
                        start_time=start_time,
                        estimated_duration_minutes=case.estimated_duration_minutes,
                        status=HearingStatus.SCHEDULED,
                        notes=f"Auto-scheduled via DCM system (priority: {-neg_priority:.2f})"
                    )

                    result.scheduled_hearings.append(hearing)

                    # Update available slots
                    available_slots[bench_id] -= case.estimated_duration_minutes

                    # Update statistics
                    daily_scheduled += 1
                    daily_duration += case.estimated_duration_minutes
                    stats["scheduled_count"] += 1
                    stats["total_duration_scheduled"] += case.estimated_duration_minutes

                else:
                    # Can't schedule today, try again later
                    temp_heap.append((neg_priority, case_id, case))

            # Put unscheduled cases back in heap for next day
            for item in temp_heap:
                heapq.heappush(case_priority_heap, item)

            # Record daily stats
            stats["scheduling_dates"].append({
                "date": current_date.isoformat(),
                "scheduled_count": daily_scheduled,
                "total_duration": daily_duration,
                "available_slots_remaining": sum(available_slots.values())
            })

        # Remaining cases are unplaced
        while case_priority_heap:
            _, _, case = heapq.heappop(case_priority_heap)
            result.unplaced_cases.append(case)
            stats["unplaced_count"] += 1

        # Calculate final statistics
        stats["placement_rate"] = (
            (stats["scheduled_count"] / stats["total_cases"]) * 100
            if stats["total_cases"] > 0 else 0
        )
        stats["average_duration_per_case"] = (
            stats["total_duration_scheduled"] / stats["scheduled_count"]
            if stats["scheduled_count"] > 0 else 0
        )

        result.scheduling_stats = stats

        return result

    def get_scheduling_conflicts(
        self,
        hearings: List[Hearing],
        target_date: date
    ) -> List[Dict[str, Any]]:
        """
        Detect scheduling conflicts for a given date

        Returns:
            List of conflict descriptions
        """
        conflicts = []
        date_hearings = [h for h in hearings if h.hearing_date == target_date]

        # Group by bench and check for overlaps
        bench_schedules = {}
        for hearing in date_hearings:
            if hearing.bench_id not in bench_schedules:
                bench_schedules[hearing.bench_id] = []
            bench_schedules[hearing.bench_id].append(hearing)

        # Check for time overlaps within each bench
        for bench_id, bench_hearings in bench_schedules.items():
            for i, hearing1 in enumerate(bench_hearings):
                for hearing2 in bench_hearings[i+1:]:
                    # Simple overlap check (would need more sophisticated logic for real times)
                    if self._hearings_overlap(hearing1, hearing2):
                        conflicts.append({
                            "type": "time_overlap",
                            "bench_id": bench_id,
                            "hearing1_id": hearing1.id,
                            "hearing2_id": hearing2.id,
                            "description": f"Hearings {hearing1.id} and {hearing2.id} overlap on bench {bench_id}"
                        })

        return conflicts

    def _hearings_overlap(self, hearing1: Hearing, hearing2: Hearing) -> bool:
        """
        Check if two hearings overlap in time
        Simplified version - in reality would need proper time calculations
        """
        # For now, just check if they're on the same day and bench
        return (hearing1.hearing_date == hearing2.hearing_date and
                hearing1.bench_id == hearing2.bench_id)


# Global instance
scheduler = CaseScheduler()

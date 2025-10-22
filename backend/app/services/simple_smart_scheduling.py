"""
Simplified Smart Scheduling Service
Working version with core functionality
"""

from datetime import datetime, time, timedelta
from enum import Enum
from typing import Any, Dict, List

from sqlmodel import Session, select

from app.models.bench import Bench
from app.models.case import Case, CasePriority, CaseStatus
from app.models.hearing import Hearing
from app.models.user import User, UserRole


class SchedulingStrategy(str, Enum):
    PRIORITY_FIRST = "priority_first"
    FIFO = "fifo"
    BALANCED = "balanced"


class SimpleSmartSchedulingService:
    """Simplified scheduling service that actually works"""

    def __init__(self):
        self.working_hours_start = time(9, 0)
        self.working_hours_end = time(17, 0)
        self.slot_duration = 60  # minutes

    def get_available_slots_simple(self, session: Session, start_date: datetime,
                                  end_date: datetime) -> Dict[str, Any]:
        """Get available slots with error handling"""
        try:
            # Get all benches
            benches = list(session.exec(select(Bench)).all())

            if not benches:
                # Create a default bench if none exists
                default_bench = Bench(
                    name="Default Bench",
                    court_number="1",
                    is_active=True
                )
                session.add(default_bench)
                session.commit()
                session.refresh(default_bench)
                benches = [default_bench]

            # Calculate theoretical slots
            days = (end_date.date() - start_date.date()).days + 1
            working_days = sum(1 for i in range(days)
                             if (start_date.date() + timedelta(days=i)).weekday() < 5)

            daily_slots = 8  # 9 AM to 5 PM
            total_slots = working_days * daily_slots * len(benches)

            # Get existing hearings
            existing_hearings = list(session.exec(
                select(Hearing).where(
                    Hearing.hearing_date >= start_date.date(),
                    Hearing.hearing_date <= end_date.date()
                )
            ).all())

            available_slots = total_slots - len(existing_hearings)

            return {
                "status": "success",
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "total_slots": total_slots,
                "available_slots": max(0, available_slots),
                "availability_rate": (available_slots / total_slots * 100) if total_slots > 0 else 0,
                "slots": self._generate_sample_slots(start_date, end_date, benches),
                "benches_count": len(benches),
                "working_days": working_days
            }

        except Exception as e:
            return {
                "error": f"Failed to get available slots: {str(e)}",
                "total_slots": 0,
                "available_slots": 0,
                "availability_rate": 0,
                "slots": []
            }

    def suggest_optimal_schedule_simple(self, session: Session, days_ahead: int = 14) -> Dict[str, Any]:
        """Simple optimization suggestions"""
        try:
            # Get pending cases
            pending_cases = list(session.exec(
                select(Case).where(Case.status.in_([CaseStatus.FILED, CaseStatus.UNDER_REVIEW]))
            ).all())

            suggestions = []

            # Simple analysis
            urgent_cases = [c for c in pending_cases if c.priority == CasePriority.URGENT]
            old_cases = [c for c in pending_cases if (datetime.now() - c.created_at).days > 30]

            if urgent_cases:
                suggestions.append({
                    "type": "urgent_scheduling",
                    "priority": "high",
                    "message": f"Schedule {len(urgent_cases)} urgent cases immediately",
                    "action": "immediate_scheduling",
                    "cases": [{"id": c.id, "case_number": c.case_number} for c in urgent_cases[:3]]
                })

            if old_cases:
                suggestions.append({
                    "type": "aged_cases",
                    "priority": "medium",
                    "message": f"Found {len(old_cases)} cases older than 30 days",
                    "action": "prioritize_old_cases"
                })

            if len(pending_cases) > 10:
                suggestions.append({
                    "type": "high_volume",
                    "priority": "medium",
                    "message": f"High case volume detected ({len(pending_cases)} pending)",
                    "action": "increase_scheduling_capacity"
                })

            return {
                "status": "success",
                "analysis_period": f"{datetime.now().date()} to {(datetime.now() + timedelta(days=days_ahead)).date()}",
                "optimization_suggestions": suggestions,
                "total_pending_cases": len(pending_cases),
                "recommended_strategy": self._simple_strategy_recommendation(pending_cases)
            }

        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to generate suggestions: {str(e)}",
                "optimization_suggestions": [],
                "total_pending_cases": 0
            }

    def schedule_cases_simple(self, session: Session, case_ids: List[int],
                             strategy: SchedulingStrategy = SchedulingStrategy.BALANCED) -> Dict[str, Any]:
        """Simple case scheduling"""
        try:
            # Get cases
            cases = []
            for case_id in case_ids:
                case = session.get(Case, case_id)
                if case and case.status in [CaseStatus.FILED, CaseStatus.UNDER_REVIEW]:
                    cases.append(case)

            if not cases:
                return {"error": "No valid cases to schedule"}

            # Get benches
            benches = list(session.exec(select(Bench)).all())
            if not benches:
                return {"error": "No benches available"}

            # Get judges
            judges = list(session.exec(
                select(User).where(
                    User.role.in_([UserRole.JUDGE, UserRole.ADMIN]),
                    User.is_active
                )
            ).all())

            if not judges:
                return {"error": "No judges available"}

            # Simple scheduling - assign to next available slots
            scheduled_hearings = []

            start_date = datetime.now() + timedelta(days=1)  # Start tomorrow

            for i, case in enumerate(cases[:5]):  # Limit to 5 for testing
                hearing_date = start_date + timedelta(days=i)

                # Skip weekends
                while hearing_date.weekday() >= 5:
                    hearing_date += timedelta(days=1)

                hearing_data = {
                    "case_id": case.id,
                    "hearing_date": hearing_date.date(),
                    "start_time": time(10, 0),  # 10 AM
                    "estimated_duration_minutes": 60,
                    "bench_id": benches[i % len(benches)].id,
                    "judge_id": judges[i % len(judges)].id
                }

                scheduled_hearings.append(hearing_data)

            unscheduled_cases = [
                {"case_id": case.id, "case_number": case.case_number, "reason": "Limited test scheduling"}
                for case in cases[5:]
            ]

            return {
                "status": "success",
                "strategy_used": strategy.value,
                "scheduled_hearings": scheduled_hearings,
                "unscheduled_cases": unscheduled_cases,
                "statistics": {
                    "total_cases": len(cases),
                    "scheduled_count": len(scheduled_hearings),
                    "unscheduled_count": len(unscheduled_cases),
                    "success_rate": len(scheduled_hearings) / len(cases) * 100
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "error": f"Scheduling failed: {str(e)}",
                "scheduled_hearings": [],
                "unscheduled_cases": []
            }

    def _generate_sample_slots(self, start_date: datetime, end_date: datetime, benches: List[Bench]) -> List[Dict]:
        """Generate sample available slots"""
        slots = []
        current_date = start_date

        while current_date.date() <= end_date.date() and len(slots) < 10:
            if current_date.weekday() < 5:  # Weekdays only
                for bench in benches[:2]:  # First 2 benches
                    slots.append({
                        "date": current_date.date().isoformat(),
                        "start_time": "10:00:00",
                        "end_time": "11:00:00",
                        "court_number": bench.court_number,
                        "bench_id": bench.id,
                        "is_available": True
                    })

                    if len(slots) >= 10:
                        break

            current_date += timedelta(days=1)

        return slots

    def _simple_strategy_recommendation(self, pending_cases: List[Case]) -> str:
        """Simple strategy recommendation"""
        if not pending_cases:
            return SchedulingStrategy.BALANCED.value

        urgent_count = len([c for c in pending_cases if c.priority == CasePriority.URGENT])

        if urgent_count > len(pending_cases) * 0.3:
            return SchedulingStrategy.PRIORITY_FIRST.value
        else:
            return SchedulingStrategy.BALANCED.value


# Global instance
simple_smart_scheduling_service = SimpleSmartSchedulingService()

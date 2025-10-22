"""
Advanced Smart Scheduling Service for DCM System
Implements intelligent case scheduling with optimization algorithms
"""

import heapq
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlmodel import Session, select

from app.models.bench import Bench
from app.models.case import Case, CasePriority, CaseStatus, CaseType
from app.models.hearing import Hearing


class SchedulingStrategy(str, Enum):
    PRIORITY_FIRST = "priority_first"
    FIFO = "fifo"
    SHORTEST_JOB_FIRST = "shortest_job_first"
    BALANCED = "balanced"
    COURT_EFFICIENCY = "court_efficiency"


@dataclass
class SchedulingSlot:
    """Represents an available time slot for scheduling"""
    date: datetime
    start_time: time
    end_time: time
    court_room: str
    bench_id: int
    estimated_duration: int  # minutes
    is_available: bool = True
    priority_weight: float = 1.0


@dataclass
class CaseSchedulingRequest:
    """Represents a case that needs to be scheduled"""
    case_id: int
    case_type: CaseType
    priority: CasePriority
    estimated_duration: int  # minutes
    preferred_dates: List[datetime] = None
    required_participants: List[int] = None  # user IDs
    complexity_score: float = 1.0
    urgency_multiplier: float = 1.0


class SmartSchedulingService:
    """Advanced scheduling service with multiple optimization strategies"""

    def __init__(self):
        self.working_hours_start = time(9, 0)  # 9:00 AM
        self.working_hours_end = time(17, 0)   # 5:00 PM
        self.slot_duration = 60  # minutes per slot
        self.lunch_break_start = time(13, 0)   # 1:00 PM
        self.lunch_break_end = time(14, 0)     # 2:00 PM

        # Priority weights for different case types
        self.priority_weights = {
            CasePriority.URGENT: 4.0,
            CasePriority.HIGH: 3.0,
            CasePriority.MEDIUM: 2.0,
            CasePriority.LOW: 1.0
        }

        # Complexity weights for different case types
        self.complexity_weights = {
            CaseType.CONSTITUTIONAL: 3.0,
            CaseType.COMMERCIAL: 2.5,
            CaseType.CRIMINAL: 2.0,
            CaseType.FAMILY: 1.8,
            CaseType.CIVIL: 1.5
        }

    def get_available_slots(self, session: Session, start_date: datetime,
                           end_date: datetime, bench_id: Optional[int] = None) -> List[SchedulingSlot]:
        """Get all available scheduling slots for the given date range"""

        # Get all benches if none specified
        if bench_id:
            benches = [session.get(Bench, bench_id)]
        else:
            benches = session.exec(select(Bench)).all()

        # Get existing hearings in the date range
        existing_hearings = session.exec(
            select(Hearing).where(
                Hearing.hearing_date >= start_date.date(),
                Hearing.hearing_date <= end_date.date()
            )
        ).all()

        # Create booking map for quick lookup
        bookings = {}
        for hearing in existing_hearings:
            key = f"{hearing.hearing_date}_{hearing.bench_id}_{hearing.start_time}"
            bookings[key] = hearing

        available_slots = []
        current_date = start_date

        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                current_date += timedelta(days=1)
                continue

            for bench in benches:
                # Generate time slots for the day
                current_time = datetime.combine(current_date.date(), self.working_hours_start)
                end_time = datetime.combine(current_date.date(), self.working_hours_end)

                while current_time < end_time:
                    slot_end = current_time + timedelta(minutes=self.slot_duration)

                    # Skip lunch break
                    if (current_time.time() >= self.lunch_break_start and
                        current_time.time() < self.lunch_break_end):
                        current_time = datetime.combine(current_date.date(), self.lunch_break_end)
                        continue

                    # Check if slot is available
                    booking_key = f"{current_date.date()}_{bench.id}_{current_time.time()}"
                    is_available = booking_key not in bookings

                    slot = SchedulingSlot(
                        date=current_date,
                        start_time=current_time.time(),
                        end_time=slot_end.time(),
                        court_room=bench.court_room,
                        bench_id=bench.id,
                        estimated_duration=self.slot_duration,
                        is_available=is_available
                    )

                    available_slots.append(slot)
                    current_time += timedelta(minutes=self.slot_duration)

            current_date += timedelta(days=1)

        return available_slots

    def calculate_case_scheduling_priority(self, case: Case, strategy: SchedulingStrategy) -> float:
        """Calculate scheduling priority score for a case based on strategy"""

        base_priority = self.priority_weights.get(case.priority, 1.0)
        complexity_weight = self.complexity_weights.get(case.case_type, 1.0)

        # Age factor (older cases get higher priority)
        age_days = (datetime.now() - case.created_at).days
        age_factor = 1.0 + (age_days / 30.0) * 0.5  # 50% bonus after 30 days

        if strategy == SchedulingStrategy.PRIORITY_FIRST:
            return base_priority * age_factor * 2.0

        elif strategy == SchedulingStrategy.FIFO:
            return age_factor * 10.0  # Age is primary factor

        elif strategy == SchedulingStrategy.SHORTEST_JOB_FIRST:
            # Estimate duration based on case type and complexity
            estimated_duration = self._estimate_case_duration(case)
            duration_factor = 100.0 / estimated_duration  # Shorter cases first
            return duration_factor * base_priority

        elif strategy == SchedulingStrategy.BALANCED:
            return (base_priority + age_factor + complexity_weight) / 3.0

        elif strategy == SchedulingStrategy.COURT_EFFICIENCY:
            # Optimize for court utilization
            efficiency_score = base_priority * complexity_weight
            return efficiency_score

        return base_priority

    def schedule_cases_optimally(self, session: Session,
                                case_ids: List[int],
                                start_date: datetime,
                                end_date: datetime,
                                strategy: SchedulingStrategy = SchedulingStrategy.BALANCED) -> Dict[str, Any]:
        """Schedule multiple cases optimally using the specified strategy"""

        # Get cases to schedule
        cases = []
        for case_id in case_ids:
            case = session.get(Case, case_id)
            if case and case.status in [CaseStatus.FILED, CaseStatus.UNDER_REVIEW]:
                cases.append(case)

        if not cases:
            return {"error": "No valid cases to schedule"}

        # Get available slots
        available_slots = [slot for slot in self.get_available_slots(session, start_date, end_date)
                          if slot.is_available]

        if not available_slots:
            return {"error": "No available slots in the specified date range"}

        # Calculate priority scores for all cases
        case_priorities = []
        for case in cases:
            priority_score = self.calculate_case_scheduling_priority(case, strategy)
            heapq.heappush(case_priorities, (-priority_score, case.id, case))  # Negative for max heap

        # Schedule cases using the chosen strategy
        scheduled_hearings = []
        unscheduled_cases = []
        slot_index = 0

        while case_priorities and slot_index < len(available_slots):
            _, case_id, case = heapq.heappop(case_priorities)

            # Find best slot for this case
            best_slot = self._find_optimal_slot_for_case(case, available_slots[slot_index:])

            if best_slot:
                # Create hearing
                hearing_data = {
                    "case_id": case.id,
                    "hearing_date": best_slot.date.date(),
                    "start_time": best_slot.start_time,
                    "estimated_duration_minutes": case.estimated_duration_minutes or 60,
                    "bench_id": best_slot.bench_id,
                    "judge_id": 1,  # Default to first available judge for now
                    "status": "scheduled"
                }

                scheduled_hearings.append(hearing_data)

                # Remove the used slot
                available_slots.remove(best_slot)
            else:
                unscheduled_cases.append({
                    "case_id": case.id,
                    "case_number": case.case_number,
                    "reason": "No suitable slot available"
                })

        # Add remaining cases to unscheduled
        while case_priorities:
            _, case_id, case = heapq.heappop(case_priorities)
            unscheduled_cases.append({
                "case_id": case.id,
                "case_number": case.case_number,
                "reason": "Insufficient slots"
            })

        return {
            "status": "success",
            "strategy_used": strategy.value,
            "scheduled_hearings": scheduled_hearings,
            "unscheduled_cases": unscheduled_cases,
            "statistics": {
                "total_cases": len(cases),
                "scheduled_count": len(scheduled_hearings),
                "unscheduled_count": len(unscheduled_cases),
                "success_rate": len(scheduled_hearings) / len(cases) * 100,
                "available_slots_used": len(scheduled_hearings),
                "remaining_slots": len(available_slots) - len(scheduled_hearings)
            }
        }

    def _find_optimal_slot_for_case(self, case: Case, available_slots: List[SchedulingSlot]) -> Optional[SchedulingSlot]:
        """Find the most suitable slot for a specific case"""
        if not available_slots:
            return None


        # Score each slot for this case
        scored_slots = []
        for slot in available_slots:
            score = self._calculate_slot_fitness(case, slot)
            scored_slots.append((score, slot))

        # Sort by score (highest first)
        scored_slots.sort(key=lambda x: x[0], reverse=True)

        # Return the best fitting slot
        return scored_slots[0][1] if scored_slots else None

    def _calculate_slot_fitness(self, case: Case, slot: SchedulingSlot) -> float:
        """Calculate how well a slot fits a case"""
        score = 0.0

        # Duration compatibility
        case_duration = case.estimated_duration_minutes or 60
        if case_duration <= slot.estimated_duration:
            score += 10.0
        else:
            score -= 5.0  # Penalty for duration mismatch

        # Priority bonus for morning slots
        if slot.start_time < time(12, 0):
            if case.priority in [CasePriority.URGENT, CasePriority.HIGH]:
                score += 5.0

        # Case type preferences
        case_type_preferences = {
            CaseType.CONSTITUTIONAL: time(10, 0),  # Complex cases in morning
            CaseType.COMMERCIAL: time(11, 0),
            CaseType.CRIMINAL: time(9, 0),        # Urgent criminal cases early
            CaseType.FAMILY: time(14, 0),         # Family cases post-lunch
            CaseType.CIVIL: time(15, 0)           # Civil cases in afternoon
        }

        preferred_time = case_type_preferences.get(case.case_type, time(10, 0))
        time_diff = abs(
            (slot.start_time.hour * 60 + slot.start_time.minute) -
            (preferred_time.hour * 60 + preferred_time.minute)
        )

        # Bonus for being close to preferred time
        score += max(0, 5.0 - (time_diff / 60.0))

        return score

    def suggest_optimal_schedule(self, session: Session, days_ahead: int = 14,
                                strategy: SchedulingStrategy = SchedulingStrategy.BALANCED) -> Dict[str, Any]:
        """Generate AI-powered scheduling optimization suggestions"""

        # Get pending cases
        pending_cases = session.exec(
            select(Case).where(Case.status.in_([CaseStatus.FILED, CaseStatus.UNDER_REVIEW]))
        ).all()

        if not pending_cases:
            return {"message": "No pending cases to schedule"}

        start_date = datetime.now()
        end_date = start_date + timedelta(days=days_ahead)

        # Analyze current schedule efficiency
        current_efficiency = self._analyze_schedule_efficiency(session, start_date, end_date)

        # Generate optimization suggestions
        suggestions = []

        # 1. Priority-based suggestions
        urgent_cases = [case for case in pending_cases if case.priority == CasePriority.URGENT]
        if urgent_cases:
            suggestions.append({
                "type": "urgent_scheduling",
                "priority": "high",
                "message": f"Schedule {len(urgent_cases)} urgent cases within next 3 days",
                "action": "immediate_scheduling",
                "cases": [{"id": c.id, "case_number": c.case_number} for c in urgent_cases[:5]]
            })

        # 2. Workload balancing suggestions
        workload_analysis = self._analyze_workload_distribution(session, start_date, end_date)
        if workload_analysis["imbalance_detected"]:
            suggestions.append({
                "type": "workload_balancing",
                "priority": "medium",
                "message": "Detected workload imbalance across benches",
                "action": "redistribute_cases",
                "details": workload_analysis
            })

        # 3. Time slot optimization
        slot_utilization = self._analyze_slot_utilization(session, start_date, end_date)
        if slot_utilization["underutilized_slots"]:
            suggestions.append({
                "type": "slot_optimization",
                "priority": "medium",
                "message": f"Found {len(slot_utilization['underutilized_slots'])} underutilized time slots",
                "action": "reschedule_for_efficiency",
                "available_slots": slot_utilization["underutilized_slots"][:10]
            })

        # 4. Strategic scheduling recommendations
        strategic_recommendations = self._generate_strategic_recommendations(pending_cases)
        suggestions.extend(strategic_recommendations)

        return {
            "status": "success",
            "analysis_period": f"{start_date.date()} to {end_date.date()}",
            "current_efficiency": current_efficiency,
            "optimization_suggestions": suggestions,
            "total_pending_cases": len(pending_cases),
            "recommended_strategy": self._recommend_best_strategy(pending_cases)
        }

    def analyze_scheduling_conflicts(self, session: Session) -> Dict[str, Any]:
        """Comprehensive analysis of scheduling conflicts and bottlenecks"""

        # Get all hearings for the next 30 days
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)

        hearings = session.exec(
            select(Hearing).where(
                Hearing.hearing_date >= start_date.date(),
                Hearing.hearing_date <= end_date.date()
            )
        ).all()

        conflicts = []

        # Check for time conflicts
        for i, hearing1 in enumerate(hearings):
            for j, hearing2 in enumerate(hearings[i+1:], i+1):
                if self._check_hearing_conflict(hearing1, hearing2):
                    conflicts.append({
                        "type": "time_conflict",
                        "severity": "high",
                        "hearing1": {
                            "id": hearing1.id,
                            "case_id": hearing1.case_id,
                            "scheduled_time": hearing1.hearing_date.isoformat()
                        },
                        "hearing2": {
                            "id": hearing2.id,
                            "case_id": hearing2.case_id,
                            "scheduled_time": hearing2.hearing_date.isoformat()
                        },
                        "reason": "Overlapping time slots"
                    })

        # Analyze capacity utilization
        capacity_analysis = self._analyze_capacity_utilization(session, start_date, end_date)

        # Generate recommendations
        recommendations = []

        if conflicts:
            recommendations.append({
                "type": "resolve_conflicts",
                "priority": "urgent",
                "message": f"Resolve {len(conflicts)} scheduling conflicts immediately",
                "action": "manual_review_required"
            })

        if capacity_analysis["utilization_rate"] > 0.9:
            recommendations.append({
                "type": "capacity_warning",
                "priority": "high",
                "message": "Court capacity approaching maximum. Consider additional resources.",
                "action": "increase_capacity"
            })

        if capacity_analysis["utilization_rate"] < 0.6:
            recommendations.append({
                "type": "underutilization",
                "priority": "medium",
                "message": "Court resources underutilized. Opportunity for more scheduling.",
                "action": "increase_scheduling"
            })

        return {
            "status": "success",
            "analysis_date": datetime.now().isoformat(),
            "conflicts": {
                "total_conflicts": len(conflicts),
                "time_conflicts": len([c for c in conflicts if c["type"] == "time_conflict"]),
                "details": conflicts
            },
            "capacity_analysis": capacity_analysis,
            "recommendations": recommendations
        }

    # Helper methods for advanced analytics
    def _analyze_schedule_efficiency(self, session: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze current schedule efficiency metrics"""

        hearings = session.exec(
            select(Hearing).where(
                Hearing.hearing_date >= start_date.date(),
                Hearing.hearing_date <= end_date.date()
            )
        ).all()

        total_slots = self._calculate_total_available_slots(start_date, end_date)
        scheduled_slots = len(hearings)

        return {
            "utilization_rate": scheduled_slots / total_slots if total_slots > 0 else 0,
            "total_available_slots": total_slots,
            "scheduled_slots": scheduled_slots,
            "efficiency_score": min(1.0, scheduled_slots / (total_slots * 0.8))  # 80% is optimal
        }

    def _analyze_workload_distribution(self, session: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze workload distribution across benches and judges"""

        hearings = session.exec(
            select(Hearing).where(
                Hearing.hearing_date >= start_date.date(),
                Hearing.hearing_date <= end_date.date()
            )
        ).all()

        bench_workload = {}
        judge_workload = {}

        for hearing in hearings:
            bench_workload[hearing.bench_id] = bench_workload.get(hearing.bench_id, 0) + 1
            if hasattr(hearing, 'judge_id') and hearing.judge_id:
                judge_workload[hearing.judge_id] = judge_workload.get(hearing.judge_id, 0) + 1

        # Calculate standard deviation to detect imbalance
        if bench_workload:
            bench_values = list(bench_workload.values())
            bench_avg = sum(bench_values) / len(bench_values)
            bench_std = (sum((x - bench_avg) ** 2 for x in bench_values) / len(bench_values)) ** 0.5

            imbalance_detected = bench_std > bench_avg * 0.3  # 30% threshold
        else:
            imbalance_detected = False

        return {
            "bench_distribution": bench_workload,
            "judge_distribution": judge_workload,
            "imbalance_detected": imbalance_detected,
            "recommendation": "redistribute_cases" if imbalance_detected else "maintain_current"
        }

    def _analyze_slot_utilization(self, session: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze time slot utilization patterns"""

        available_slots = self.get_available_slots(session, start_date, end_date)
        underutilized_slots = [slot for slot in available_slots if slot.is_available]

        # Find time patterns
        morning_slots = [s for s in underutilized_slots if s.start_time < time(12, 0)]
        afternoon_slots = [s for s in underutilized_slots if s.start_time >= time(14, 0)]

        return {
            "underutilized_slots": underutilized_slots,
            "patterns": {
                "morning_availability": len(morning_slots),
                "afternoon_availability": len(afternoon_slots),
                "peak_available_time": self._find_peak_available_time(underutilized_slots)
            }
        }

    def _generate_strategic_recommendations(self, pending_cases: List[Case]) -> List[Dict[str, Any]]:
        """Generate strategic scheduling recommendations based on case analysis"""

        recommendations = []

        # Analyze case types
        case_type_counts = {}
        for case in pending_cases:
            case_type_counts[case.case_type] = case_type_counts.get(case.case_type, 0) + 1

        # Check for case type clustering opportunities
        if case_type_counts.get(CaseType.COMMERCIAL, 0) >= 3:
            recommendations.append({
                "type": "case_clustering",
                "priority": "low",
                "message": f"Consider clustering {case_type_counts[CaseType.COMMERCIAL]} commercial cases for efficiency",
                "action": "schedule_similar_cases_together"
            })

        # Check for urgent case accumulation
        urgent_count = len([c for c in pending_cases if c.priority == CasePriority.URGENT])
        if urgent_count > 5:
            recommendations.append({
                "type": "urgent_backlog",
                "priority": "high",
                "message": f"High urgent case backlog ({urgent_count} cases). Consider emergency scheduling.",
                "action": "emergency_scheduling_session"
            })

        return recommendations

    def _recommend_best_strategy(self, pending_cases: List[Case]) -> str:
        """Recommend the best scheduling strategy based on current case load"""

        if not pending_cases:
            return SchedulingStrategy.BALANCED.value

        urgent_count = len([c for c in pending_cases if c.priority == CasePriority.URGENT])
        old_cases = len([c for c in pending_cases if (datetime.now() - c.created_at).days > 30])

        # Decision logic
        if urgent_count > len(pending_cases) * 0.3:  # More than 30% urgent
            return SchedulingStrategy.PRIORITY_FIRST.value
        elif old_cases > len(pending_cases) * 0.4:  # More than 40% old cases
            return SchedulingStrategy.FIFO.value
        else:
            return SchedulingStrategy.BALANCED.value

    def _calculate_total_available_slots(self, start_date: datetime, end_date: datetime) -> int:
        """Calculate total theoretical available slots in date range"""

        total_days = (end_date - start_date).days
        working_days = total_days - (total_days // 7) * 2  # Remove weekends

        # Calculate daily slots (9 AM to 5 PM with 1 hour lunch break)
        daily_hours = 7  # 8 hours - 1 hour lunch
        slots_per_day = daily_hours

        # Assume 3 benches on average
        benches_count = 3

        return working_days * slots_per_day * benches_count

    def _check_hearing_conflict(self, hearing1: Hearing, hearing2: Hearing) -> bool:
        """Check if two hearings have scheduling conflicts"""

        # Same date and bench conflict
        if (hearing1.hearing_date == hearing2.hearing_date and
            hearing1.bench_id == hearing2.bench_id):

            # Check time overlap
            h1_start = datetime.combine(hearing1.hearing_date, hearing1.start_time)
            h1_end = h1_start + timedelta(minutes=hearing1.estimated_duration_minutes or 60)

            h2_start = datetime.combine(hearing2.hearing_date, hearing2.start_time)
            h2_end = h2_start + timedelta(minutes=hearing2.estimated_duration_minutes or 60)

            return not (h1_end <= h2_start or h2_end <= h1_start)

        return False

    def _analyze_capacity_utilization(self, session: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze overall capacity utilization"""

        total_slots = self._calculate_total_available_slots(start_date, end_date)

        hearings = session.exec(
            select(Hearing).where(
                Hearing.hearing_date >= start_date.date(),
                Hearing.hearing_date <= end_date.date()
            )
        ).all()

        scheduled_slots = len(hearings)
        utilization_rate = scheduled_slots / total_slots if total_slots > 0 else 0

        return {
            "utilization_rate": utilization_rate,
            "total_capacity": total_slots,
            "scheduled_slots": scheduled_slots,
            "available_slots": total_slots - scheduled_slots,
            "status": "optimal" if 0.7 <= utilization_rate <= 0.9 else
                     "underutilized" if utilization_rate < 0.7 else "overutilized"
        }

    def _find_peak_available_time(self, slots: List[SchedulingSlot]) -> str:
        """Find the time period with most available slots"""

        if not slots:
            return "No available slots"

        time_periods = {
            "morning": len([s for s in slots if s.start_time < time(12, 0)]),
            "afternoon": len([s for s in slots if s.start_time >= time(14, 0)]),
            "early_morning": len([s for s in slots if s.start_time < time(11, 0)])
        }

        return max(time_periods, key=time_periods.get)

    def _estimate_case_duration(self, case: Case) -> int:
        """Estimate case duration based on type and complexity"""

        base_durations = {
            CaseType.CONSTITUTIONAL: 180,  # 3 hours
            CaseType.COMMERCIAL: 120,     # 2 hours
            CaseType.CRIMINAL: 90,        # 1.5 hours
            CaseType.FAMILY: 75,          # 1.25 hours
            CaseType.CIVIL: 60            # 1 hour
        }

        base_duration = base_durations.get(case.case_type, 60)

        # Adjust for priority (urgent cases might be expedited)
        if case.priority == CasePriority.URGENT:
            base_duration = int(base_duration * 0.8)  # 20% faster handling
        elif case.priority == CasePriority.LOW:
            base_duration = int(base_duration * 1.2)  # 20% more time

        return case.estimated_duration_minutes or base_duration

        # Calculate priorities and create scheduling requests
        scheduling_requests = []
        for case in cases:
            priority_score = self.calculate_case_scheduling_priority(case, strategy)
            estimated_duration = self._estimate_case_duration(case)

            request = CaseSchedulingRequest(
                case_id=case.id,
                case_type=case.case_type,
                priority=case.priority,
                estimated_duration=estimated_duration,
                complexity_score=priority_score
            )
            scheduling_requests.append(request)

        # Sort by priority (higher score = higher priority)
        scheduling_requests.sort(key=lambda x: x.complexity_score, reverse=True)

        # Assign slots to cases
        scheduled_hearings = []
        used_slots = set()

        for request in scheduling_requests:
            best_slot = self._find_best_slot(request, available_slots, used_slots, strategy)

            if best_slot:
                # Create hearing
                hearing = Hearing(
                    case_id=request.case_id,
                    bench_id=best_slot.bench_id,
                    scheduled_date=best_slot.date,
                    scheduled_time=best_slot.start_time,
                    estimated_duration=request.estimated_duration,
                    status="scheduled"
                )

                scheduled_hearings.append({
                    "hearing": hearing,
                    "slot": best_slot,
                    "case_id": request.case_id,
                    "priority_score": request.complexity_score
                })

                # Mark slot as used
                slot_key = f"{best_slot.date.date()}_{best_slot.bench_id}_{best_slot.start_time}"
                used_slots.add(slot_key)

        # Save hearings to database
        for scheduled in scheduled_hearings:
            session.add(scheduled["hearing"])

        session.commit()

        return {
            "status": "success",
            "strategy_used": strategy.value,
            "total_cases": len(cases),
            "successfully_scheduled": len(scheduled_hearings),
            "failed_to_schedule": len(cases) - len(scheduled_hearings),
            "scheduled_hearings": [
                {
                    "case_id": s["case_id"],
                    "date": s["slot"].date.isoformat(),
                    "time": s["slot"].start_time.isoformat(),
                    "court_room": s["slot"].court_room,
                    "priority_score": round(s["priority_score"], 2)
                }
                for s in scheduled_hearings
            ],
            "optimization_metrics": {
                "average_priority_score": sum(s["priority_score"] for s in scheduled_hearings) / len(scheduled_hearings) if scheduled_hearings else 0,
                "court_utilization": len(scheduled_hearings) / len(available_slots) * 100 if available_slots else 0,
                "scheduling_efficiency": len(scheduled_hearings) / len(cases) * 100
            }
        }

    def suggest_optimal_schedule(self, session: Session,
                               days_ahead: int = 14,
                               strategy: SchedulingStrategy = SchedulingStrategy.BALANCED) -> Dict[str, Any]:
        """Suggest optimal schedule for pending cases in the next specified days"""

        # Get all cases that need scheduling
        pending_cases = session.exec(
            select(Case).where(
                Case.status.in_([CaseStatus.FILED, CaseStatus.UNDER_REVIEW])
            )
        ).all()

        if not pending_cases:
            return {"message": "No pending cases to schedule"}

        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=days_ahead)

        case_ids = [case.id for case in pending_cases]

        return self.schedule_cases_optimally(
            session, case_ids, start_date, end_date, strategy
        )

    def analyze_scheduling_conflicts(self, session: Session) -> Dict[str, Any]:
        """Analyze potential scheduling conflicts and overlaps"""

        # Get all scheduled hearings
        hearings = session.exec(select(Hearing)).all()

        conflicts = []
        overlaps = []

        for i, hearing1 in enumerate(hearings):
            for hearing2 in hearings[i+1:]:
                # Check for same time slot conflicts
                if (hearing1.scheduled_date == hearing2.scheduled_date and
                    hearing1.scheduled_time == hearing2.scheduled_time and
                    hearing1.bench_id == hearing2.bench_id):

                    conflicts.append({
                        "type": "double_booking",
                        "hearing1_id": hearing1.id,
                        "hearing2_id": hearing2.id,
                        "date": hearing1.scheduled_date.isoformat(),
                        "time": hearing1.scheduled_time.isoformat(),
                        "court_room": hearing1.bench.court_room if hearing1.bench else "Unknown"
                    })

                # Check for overlapping time periods
                if (hearing1.scheduled_date == hearing2.scheduled_date and
                    hearing1.bench_id == hearing2.bench_id):

                    end_time1 = (datetime.combine(hearing1.scheduled_date, hearing1.scheduled_time) +
                                timedelta(minutes=hearing1.estimated_duration or 60))
                    start_time2 = datetime.combine(hearing2.scheduled_date, hearing2.scheduled_time)

                    if start_time2 < end_time1:
                        overlaps.append({
                            "type": "time_overlap",
                            "hearing1_id": hearing1.id,
                            "hearing2_id": hearing2.id,
                            "overlap_duration": (end_time1 - start_time2).total_seconds() / 60
                        })

        # Analyze resource utilization
        bench_utilization = {}
        for hearing in hearings:
            bench_id = hearing.bench_id
            if bench_id not in bench_utilization:
                bench_utilization[bench_id] = []
            bench_utilization[bench_id].append(hearing)

        return {
            "conflict_analysis": {
                "total_conflicts": len(conflicts),
                "total_overlaps": len(overlaps),
                "conflicts": conflicts,
                "overlaps": overlaps
            },
            "resource_utilization": {
                "bench_utilization": {
                    bench_id: {
                        "hearing_count": len(hearings_list),
                        "utilization_percentage": len(hearings_list) / 40 * 100  # Assuming 40 slots per week
                    }
                    for bench_id, hearings_list in bench_utilization.items()
                }
            },
            "recommendations": [
                "Consider adding more time slots for high-utilization benches",
                "Implement buffer time between hearings to prevent overlaps",
                "Review case duration estimates for better scheduling"
            ]
        }

    def _estimate_case_duration(self, case: Case) -> int:
        """Estimate case duration in minutes based on case type and complexity"""

        base_durations = {
            CaseType.CONSTITUTIONAL: 120,  # 2 hours
            CaseType.COMMERCIAL: 90,       # 1.5 hours
            CaseType.CRIMINAL: 75,         # 1.25 hours
            CaseType.FAMILY: 60,           # 1 hour
            CaseType.CIVIL: 60             # 1 hour
        }

        base_duration = base_durations.get(case.case_type, 60)

        # Adjust based on priority
        priority_multipliers = {
            CasePriority.URGENT: 1.5,
            CasePriority.HIGH: 1.2,
            CasePriority.MEDIUM: 1.0,
            CasePriority.LOW: 0.8
        }

        multiplier = priority_multipliers.get(case.priority, 1.0)

        # Adjust based on description length (complexity indicator)
        if len(case.description) > 1000:
            multiplier *= 1.3
        elif len(case.description) > 500:
            multiplier *= 1.1

        return int(base_duration * multiplier)

    def _find_best_slot(self, request: CaseSchedulingRequest,
                       available_slots: List[SchedulingSlot],
                       used_slots: set, strategy: SchedulingStrategy) -> Optional[SchedulingSlot]:
        """Find the best available slot for a case based on strategy"""

        eligible_slots = []

        for slot in available_slots:
            slot_key = f"{slot.date.date()}_{slot.bench_id}_{slot.start_time}"
            if slot_key not in used_slots and slot.is_available:
                # Calculate slot score based on strategy
                score = self._calculate_slot_score(request, slot, strategy)
                eligible_slots.append((score, slot))

        if not eligible_slots:
            return None

        # Return slot with highest score
        eligible_slots.sort(key=lambda x: x[0], reverse=True)
        return eligible_slots[0][1]

    def _calculate_slot_score(self, request: CaseSchedulingRequest,
                            slot: SchedulingSlot, strategy: SchedulingStrategy) -> float:
        """Calculate how well a slot matches a case scheduling request"""

        score = 0.0

        # Prefer earlier slots for urgent cases
        if request.priority == CasePriority.URGENT:
            hour_score = (17 - slot.start_time.hour) / 8.0  # Earlier is better
            score += hour_score * 2.0

        # Prefer appropriate duration match
        duration_diff = abs(slot.estimated_duration - request.estimated_duration)
        duration_score = max(0, 1.0 - duration_diff / 60.0)
        score += duration_score

        # Strategy-specific scoring
        if strategy == SchedulingStrategy.COURT_EFFICIENCY:
            # Prefer slots that maximize court utilization
            score += 1.0 if slot.start_time.hour in [9, 10, 15, 16] else 0.5

        elif strategy == SchedulingStrategy.PRIORITY_FIRST:
            # Heavy weight on case priority
            score += request.complexity_score * 0.5

        return score


# Global scheduling service instance
smart_scheduling_service = SmartSchedulingService()

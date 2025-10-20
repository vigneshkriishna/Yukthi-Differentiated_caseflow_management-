"""
Advanced Analytics Service for DCM System
Provides comprehensive analytics and reporting functionality
"""

from typing import Dict, List, Any, Optional
from sqlmodel import Session, select, text
from datetime import datetime, timedelta
from app.models.case import Case, CaseStatus, CaseType, CasePriority
from app.models.user import User, UserRole
from app.models.audit_log import AuditLog, AuditAction
from app.models.hearing import Hearing
import json


class AnalyticsService:
    """Advanced analytics service for comprehensive system insights"""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes cache
        self._cache = {}
    
    def get_dashboard_overview(self, session: Session, user_id: int = None) -> Dict[str, Any]:
        """Get comprehensive dashboard overview with key metrics"""
        
        # Basic counts
        total_cases = session.exec(select(Case)).all()
        total_users = session.exec(select(User)).all()
        total_hearings = session.exec(select(Hearing)).all()
        
        # Status distribution
        status_counts = {}
        for status in CaseStatus:
            count = len([c for c in total_cases if c.status == status])
            status_counts[status.value] = count
        
        # Priority distribution  
        priority_counts = {}
        for priority in CasePriority:
            count = len([c for c in total_cases if c.priority == priority])
            priority_counts[priority.value] = count
            
        # Case type distribution
        type_counts = {}
        for case_type in CaseType:
            count = len([c for c in total_cases if c.case_type == case_type])
            type_counts[case_type.value] = count
        
        # Recent activity (last 7 days)
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_cases = [c for c in total_cases if c.created_at >= seven_days_ago]
        recent_activity = len(recent_cases)
        
        # BNS section analysis
        bns_sections = {}
        for case in total_cases:
            if hasattr(case, 'predicted_bns_section') and case.predicted_bns_section:
                section = case.predicted_bns_section
                bns_sections[section] = bns_sections.get(section, 0) + 1
        
        # User role distribution
        role_counts = {}
        for role in UserRole:
            count = len([u for u in total_users if u.role == role])
            role_counts[role.value] = count
        
        return {
            "overview": {
                "total_cases": len(total_cases),
                "total_users": len(total_users),
                "total_hearings": len(total_hearings),
                "recent_activity": recent_activity,
                "system_uptime": "99.9%",  # Mock data
                "last_updated": datetime.now().isoformat()
            },
            "case_distribution": {
                "by_status": status_counts,
                "by_priority": priority_counts,
                "by_type": type_counts
            },
            "bns_analytics": {
                "top_sections": dict(sorted(bns_sections.items(), key=lambda x: x[1], reverse=True)[:10]),
                "total_sections_used": len(bns_sections),
                "average_confidence": 0.78  # Mock data - should calculate from actual predictions
            },
            "user_analytics": {
                "by_role": role_counts,
                "active_users_today": len([u for u in total_users if u.is_active]),
                "new_users_this_week": len([u for u in total_users if u.created_at >= seven_days_ago])
            },
            "performance_metrics": {
                "average_case_processing_time": "12.5 days",  # Mock - calculate from actual data
                "cases_resolved_this_month": len([c for c in total_cases if c.status == CaseStatus.DISPOSED]),
                "pending_cases": len([c for c in total_cases if c.status in [CaseStatus.FILED, CaseStatus.UNDER_REVIEW]]),
                "hearing_success_rate": "94.2%"  # Mock data
            }
        }
    
    def get_case_analytics(self, session: Session, days: int = 30) -> Dict[str, Any]:
        """Get detailed case analytics for specified time period"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        cases = session.exec(select(Case).where(Case.created_at >= cutoff_date)).all()
        
        # Time series data (cases per day)
        daily_cases = {}
        for case in cases:
            date_key = case.created_at.strftime("%Y-%m-%d")
            daily_cases[date_key] = daily_cases.get(date_key, 0) + 1
        
        # Case resolution timeline
        resolution_times = []
        for case in cases:
            if case.status == CaseStatus.DISPOSED and hasattr(case, 'disposed_at'):
                if case.disposed_at:
                    resolution_time = (case.disposed_at - case.created_at).days
                    resolution_times.append(resolution_time)
        
        avg_resolution = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        # Complexity analysis
        complexity_distribution = {
            "simple": len([c for c in cases if self._get_case_complexity(c) == "simple"]),
            "medium": len([c for c in cases if self._get_case_complexity(c) == "medium"]), 
            "complex": len([c for c in cases if self._get_case_complexity(c) == "complex"])
        }
        
        return {
            "period": f"Last {days} days",
            "total_cases": len(cases),
            "daily_trend": daily_cases,
            "resolution_metrics": {
                "average_resolution_days": round(avg_resolution, 1),
                "fastest_resolution": min(resolution_times) if resolution_times else 0,
                "slowest_resolution": max(resolution_times) if resolution_times else 0,
                "total_resolved": len(resolution_times)
            },
            "complexity_analysis": complexity_distribution,
            "success_metrics": {
                "cases_on_time": len([c for c in cases if self._is_case_on_time(c)]),
                "delayed_cases": len([c for c in cases if self._is_case_delayed(c)]),
                "escalated_cases": len([c for c in cases if c.priority == CasePriority.URGENT])
            }
        }
    
    def get_bns_classification_analytics(self, session: Session) -> Dict[str, Any]:
        """Get analytics specific to BNS classification performance"""
        
        cases = session.exec(select(Case)).all()
        
        # BNS section frequency
        section_frequency = {}
        confidence_scores = []
        classification_success = 0
        
        for case in cases:
            # Mock BNS data - in real implementation, this would come from case.bns_prediction
            if hasattr(case, 'predicted_bns_section') and case.predicted_bns_section:
                section = case.predicted_bns_section
                section_frequency[section] = section_frequency.get(section, 0) + 1
                classification_success += 1
                
                # Mock confidence score
                confidence_scores.append(0.75 + (hash(case.id) % 25) / 100)  # Mock: 0.75-1.0 range
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Section categories
        section_categories = {
            "violent_crimes": len([s for s in section_frequency.keys() if s in ["326", "302", "307", "323"]]),
            "property_crimes": len([s for s in section_frequency.keys() if s in ["378", "379", "380", "381"]]),
            "fraud_crimes": len([s for s in section_frequency.keys() if s in ["417", "418", "419", "420"]]),
            "cyber_crimes": len([s for s in section_frequency.keys() if s in ["66", "66A", "66C", "66D"]]),
            "other_crimes": len([s for s in section_frequency.keys() if s not in ["326", "302", "307", "323", "378", "379", "380", "381", "417", "418", "419", "420", "66", "66A", "66C", "66D"]])
        }
        
        return {
            "classification_overview": {
                "total_cases_classified": classification_success,
                "classification_rate": round(classification_success / len(cases) * 100, 1) if cases else 0,
                "average_confidence": round(avg_confidence, 3),
                "unique_sections_identified": len(section_frequency)
            },
            "section_frequency": dict(sorted(section_frequency.items(), key=lambda x: x[1], reverse=True)),
            "section_categories": section_categories,
            "model_performance": {
                "high_confidence_predictions": len([c for c in confidence_scores if c > 0.8]),
                "medium_confidence_predictions": len([c for c in confidence_scores if 0.6 <= c <= 0.8]),
                "low_confidence_predictions": len([c for c in confidence_scores if c < 0.6]),
                "model_accuracy": "73.8%",  # From our actual model
                "model_status": "Operational"
            },
            "trends": {
                "most_common_crime_type": max(section_categories, key=section_categories.get) if section_categories else "N/A",
                "emerging_patterns": ["Increase in cyber crimes", "More complex fraud cases"],  # Mock insights
                "recommendation": "Consider specialized training for cyber crime BNS sections"
            }
        }
    
    def get_user_activity_analytics(self, session: Session) -> Dict[str, Any]:
        """Get analytics about user activity and system usage"""
        
        # Get audit logs for activity analysis
        recent_logs = session.exec(
            select(AuditLog).where(
                AuditLog.timestamp >= datetime.now() - timedelta(days=30)
            )
        ).all()
        
        # Activity by user role
        activity_by_role = {}
        for log in recent_logs:
            if log.user_id:
                user = session.get(User, log.user_id)
                if user:
                    role = user.role.value
                    activity_by_role[role] = activity_by_role.get(role, 0) + 1
        
        # Activity by action type
        activity_by_action = {}
        for log in recent_logs:
            action = log.action.value
            activity_by_action[action] = activity_by_action.get(action, 0) + 1
        
        # Daily activity trend
        daily_activity = {}
        for log in recent_logs:
            date_key = log.timestamp.strftime("%Y-%m-%d")
            daily_activity[date_key] = daily_activity.get(date_key, 0) + 1
        
        # Active users
        active_users = set([log.user_id for log in recent_logs if log.user_id])
        
        return {
            "activity_overview": {
                "total_actions_30_days": len(recent_logs),
                "unique_active_users": len(active_users),
                "average_daily_actions": round(len(recent_logs) / 30, 1),
                "most_active_day": max(daily_activity, key=daily_activity.get) if daily_activity else "N/A"
            },
            "activity_by_role": activity_by_role,
            "activity_by_action": activity_by_action,
            "daily_trend": daily_activity,
            "user_engagement": {
                "highly_active_users": len([uid for uid in active_users if len([l for l in recent_logs if l.user_id == uid]) > 50]),
                "moderately_active_users": len([uid for uid in active_users if 10 <= len([l for l in recent_logs if l.user_id == uid]) <= 50]),
                "low_activity_users": len([uid for uid in active_users if len([l for l in recent_logs if l.user_id == uid]) < 10])
            }
        }
    
    def get_court_schedule_analytics(self, session: Session) -> Dict[str, Any]:
        """Get analytics about court scheduling and hearing management"""
        
        hearings = session.exec(select(Hearing)).all()
        
        # Hearing status distribution
        status_distribution = {}
        for hearing in hearings:
            status = hearing.status.value if hasattr(hearing, 'status') else "scheduled"
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        # Court utilization (mock data for now)
        court_utilization = {
            "Court Room 1": {"scheduled": 25, "capacity": 30, "utilization": 83.3},
            "Court Room 2": {"scheduled": 22, "capacity": 30, "utilization": 73.3},
            "Court Room 3": {"scheduled": 28, "capacity": 30, "utilization": 93.3},
            "Court Room 4": {"scheduled": 20, "capacity": 30, "utilization": 66.7},
            "Court Room 5": {"scheduled": 26, "capacity": 30, "utilization": 86.7}
        }
        
        # Hearing timing analysis
        timing_analysis = {
            "morning_slots": len([h for h in hearings if 9 <= (h.scheduled_time.hour if hasattr(h, 'scheduled_time') else 10) < 12]),
            "afternoon_slots": len([h for h in hearings if 12 <= (h.scheduled_time.hour if hasattr(h, 'scheduled_time') else 14) < 17]),
            "total_scheduled": len(hearings)
        }
        
        return {
            "schedule_overview": {
                "total_hearings": len(hearings),
                "hearings_this_week": len([h for h in hearings if self._is_this_week(h.scheduled_date)]) if hearings else 0,
                "average_hearings_per_day": round(len(hearings) / 30, 1),  # Mock: last 30 days
                "schedule_conflicts": 2  # Mock data
            },
            "hearing_status": status_distribution,
            "court_utilization": court_utilization,
            "timing_analysis": timing_analysis,
            "efficiency_metrics": {
                "on_time_hearings": "89.2%",  # Mock
                "postponed_hearings": "6.3%",   # Mock
                "cancelled_hearings": "4.5%",   # Mock
                "average_hearing_duration": "45 minutes"  # Mock
            }
        }
    
    def _get_case_complexity(self, case: Case) -> str:
        """Determine case complexity based on various factors"""
        # Simple heuristic - in real implementation, this would be more sophisticated
        complexity_score = 0
        
        # Check description length
        if len(case.description) > 500:
            complexity_score += 2
        elif len(case.description) > 200:
            complexity_score += 1
            
        # Check case type
        if case.case_type in [CaseType.CONSTITUTIONAL, CaseType.COMMERCIAL]:
            complexity_score += 2
        elif case.case_type == CaseType.FAMILY:
            complexity_score += 1
            
        # Check priority
        if case.priority == CasePriority.URGENT:
            complexity_score += 1
            
        if complexity_score >= 4:
            return "complex"
        elif complexity_score >= 2:
            return "medium"
        else:
            return "simple"
    
    def _is_case_on_time(self, case: Case) -> bool:
        """Check if case is progressing on time"""
        # Mock implementation - would check against expected timelines
        days_since_filing = (datetime.now() - case.created_at).days
        
        if case.status == CaseStatus.FILED and days_since_filing <= 7:
            return True
        elif case.status == CaseStatus.UNDER_REVIEW and days_since_filing <= 30:
            return True
        elif case.status == CaseStatus.SCHEDULED and days_since_filing <= 60:
            return True
        
        return False
    
    def _is_case_delayed(self, case: Case) -> bool:
        """Check if case is delayed beyond expected timelines"""
        return not self._is_case_on_time(case)
    
    def _is_this_week(self, date: datetime) -> bool:
        """Check if date falls within current week"""
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return start_of_week <= date <= end_of_week


# Global analytics service instance
analytics_service = AnalyticsService()
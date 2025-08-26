"""
Audit logging service for tracking all system mutations
Records actor, action, before/after state for compliance and debugging
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
from sqlmodel import Session, select
from app.models.audit_log import AuditLog, AuditLogCreate, AuditAction
from app.models.user import User
from app.core.database import get_session


class AuditService:
    """Service for creating and managing audit logs"""
    
    def __init__(self):
        self.session_factory = get_session
    
    def log_action(
        self,
        session: Session,
        action: AuditAction,
        user: Optional[User] = None,
        resource_type: str = "unknown",
        resource_id: Optional[int] = None,
        before_data: Optional[Dict[str, Any]] = None,
        after_data: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        case_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log an auditable action
        
        Args:
            session: Database session
            action: Type of action performed
            user: User who performed the action
            resource_type: Type of resource affected (e.g., "case", "user")
            resource_id: ID of the affected resource
            before_data: State before the action
            after_data: State after the action
            description: Human-readable description
            case_id: Related case ID (if applicable)
            ip_address: User's IP address
            user_agent: User's browser/client info
            
        Returns:
            Created AuditLog record
        """
        # Serialize data to JSON
        before_json = json.dumps(before_data, default=str) if before_data else None
        after_json = json.dumps(after_data, default=str) if after_data else None
        
        # Create audit log entry
        audit_log = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            before_data=before_json,
            after_data=after_json,
            description=description,
            user_id=user.id if user else None,
            case_id=case_id,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.utcnow()
        )
        
        session.add(audit_log)
        session.commit()
        session.refresh(audit_log)
        
        return audit_log
    
    def log_case_creation(
        self,
        session: Session,
        user: User,
        case_data: Dict[str, Any],
        case_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Log case creation"""
        return self.log_action(
            session=session,
            action=AuditAction.CREATE,
            user=user,
            resource_type="case",
            resource_id=case_id,
            after_data=case_data,
            description=f"Case {case_data.get('case_number')} created",
            case_id=case_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_case_update(
        self,
        session: Session,
        user: User,
        case_id: int,
        before_data: Dict[str, Any],
        after_data: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Log case update"""
        # Identify what changed
        changes = []
        for key in set(before_data.keys()) | set(after_data.keys()):
            before_val = before_data.get(key)
            after_val = after_data.get(key)
            if before_val != after_val:
                changes.append(f"{key}: {before_val} → {after_val}")
        
        description = f"Case updated: {', '.join(changes)}" if changes else "Case updated"
        
        return self.log_action(
            session=session,
            action=AuditAction.UPDATE,
            user=user,
            resource_type="case",
            resource_id=case_id,
            before_data=before_data,
            after_data=after_data,
            description=description,
            case_id=case_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_case_classification(
        self,
        session: Session,
        user: User,
        case_id: int,
        classification_result: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Log case classification"""
        return self.log_action(
            session=session,
            action=AuditAction.CLASSIFY_CASE,
            user=user,
            resource_type="case",
            resource_id=case_id,
            after_data=classification_result,
            description=f"Case classified as {classification_result.get('track')} track",
            case_id=case_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_track_override(
        self,
        session: Session,
        user: User,
        case_id: int,
        old_track: str,
        new_track: str,
        reason: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Log track override by judge"""
        return self.log_action(
            session=session,
            action=AuditAction.OVERRIDE_TRACK,
            user=user,
            resource_type="case",
            resource_id=case_id,
            before_data={"track": old_track},
            after_data={"track": new_track, "reason": reason},
            description=f"Track overridden from {old_track} to {new_track}: {reason}",
            case_id=case_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_hearing_scheduled(
        self,
        session: Session,
        user: User,
        hearing_data: Dict[str, Any],
        hearing_id: int,
        case_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Log hearing scheduling"""
        return self.log_action(
            session=session,
            action=AuditAction.SCHEDULE_HEARING,
            user=user,
            resource_type="hearing",
            resource_id=hearing_id,
            after_data=hearing_data,
            description=f"Hearing scheduled for case on {hearing_data.get('hearing_date')}",
            case_id=case_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_user_login(
        self,
        session: Session,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Log user login"""
        return self.log_action(
            session=session,
            action=AuditAction.LOGIN,
            user=user,
            resource_type="user",
            resource_id=user.id,
            description=f"User {user.username} logged in",
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_user_logout(
        self,
        session: Session,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Log user logout"""
        return self.log_action(
            session=session,
            action=AuditAction.LOGOUT,
            user=user,
            resource_type="user",
            resource_id=user.id,
            description=f"User {user.username} logged out",
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_report_generation(
        self,
        session: Session,
        user: User,
        report_type: str,
        report_params: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Log report generation"""
        return self.log_action(
            session=session,
            action=AuditAction.GENERATE_REPORT,
            user=user,
            resource_type="report",
            after_data={"report_type": report_type, "parameters": report_params},
            description=f"Generated {report_type} report",
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def get_audit_trail(
        self,
        session: Session,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        case_id: Optional[int] = None,
        user_id: Optional[int] = None,
        action: Optional[AuditAction] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Get audit trail with filtering options
        
        Args:
            session: Database session
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            case_id: Filter by case ID
            user_id: Filter by user ID
            action: Filter by action type
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of records to return
            
        Returns:
            List of AuditLog records
        """
        statement = select(AuditLog)
        
        # Apply filters
        if resource_type:
            statement = statement.where(AuditLog.resource_type == resource_type)
        if resource_id:
            statement = statement.where(AuditLog.resource_id == resource_id)
        if case_id:
            statement = statement.where(AuditLog.case_id == case_id)
        if user_id:
            statement = statement.where(AuditLog.user_id == user_id)
        if action:
            statement = statement.where(AuditLog.action == action)
        if start_date:
            statement = statement.where(AuditLog.created_at >= start_date)
        if end_date:
            statement = statement.where(AuditLog.created_at <= end_date)
        
        # Order by most recent first and limit
        statement = statement.order_by(AuditLog.created_at.desc()).limit(limit)
        
        return list(session.exec(statement).all())
    
    def get_case_audit_summary(
        self,
        session: Session,
        case_id: int
    ) -> Dict[str, Any]:
        """
        Get audit summary for a specific case
        
        Args:
            session: Database session
            case_id: Case ID to get summary for
            
        Returns:
            Summary of audit activities for the case
        """
        statement = select(AuditLog).where(AuditLog.case_id == case_id)
        audit_logs = list(session.exec(statement).all())
        
        # Group by action type
        action_counts = {}
        first_action = None
        last_action = None
        
        for log in audit_logs:
            action_counts[log.action.value] = action_counts.get(log.action.value, 0) + 1
            
            if first_action is None or log.created_at < first_action.created_at:
                first_action = log
            if last_action is None or log.created_at > last_action.created_at:
                last_action = log
        
        return {
            "case_id": case_id,
            "total_audit_entries": len(audit_logs),
            "action_counts": action_counts,
            "first_action": {
                "action": first_action.action.value,
                "user_id": first_action.user_id,
                "timestamp": first_action.created_at
            } if first_action else None,
            "last_action": {
                "action": last_action.action.value,
                "user_id": last_action.user_id,
                "timestamp": last_action.created_at
            } if last_action else None
        }


# Global instance
audit_service = AuditService()

"""
Cases router for case management operations
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import get_current_user, require_clerk, require_judge
from app.models.user import User
from app.models.case import (
    Case, CaseCreate, CaseUpdate, CasePublic, 
    CaseStatus, CaseTrack, CaseOverride
)
from app.services.dcm_rules import dcm_engine
from app.services.nlp import bns_assist
from app.services.audit import audit_service
from datetime import datetime


router = APIRouter()


@router.post("/", response_model=CasePublic)
async def create_case(
    case_data: CaseCreate,
    request: Request,
    current_user: User = Depends(require_clerk),
    session: Session = Depends(get_session)
):
    """
    Create a new case (Clerk access required)
    """
    # Check if case number already exists
    statement = select(Case).where(Case.case_number == case_data.case_number)
    existing_case = session.exec(statement).first()
    
    if existing_case:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Case number {case_data.case_number} already exists"
        )
    
    # Create new case
    db_case = Case(**case_data.dict())
    session.add(db_case)
    session.commit()
    session.refresh(db_case)
    
    # Log case creation
    audit_service.log_case_creation(
        session=session,
        user=current_user,
        case_data=case_data.dict(),
        case_id=db_case.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return db_case


@router.get("/", response_model=List[CasePublic])
async def list_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[CaseStatus] = None,
    track: Optional[CaseTrack] = None,
    assigned_clerk_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    List cases with optional filtering
    """
    statement = select(Case)
    
    # Apply filters
    if status:
        statement = statement.where(Case.status == status)
    if track:
        statement = statement.where(Case.track == track)
    if assigned_clerk_id:
        statement = statement.where(Case.assigned_clerk_id == assigned_clerk_id)
    
    # Role-based filtering
    if current_user.role == "clerk":
        # Clerks can only see cases assigned to them
        statement = statement.where(Case.assigned_clerk_id == current_user.id)
    
    # Apply pagination
    statement = statement.offset(skip).limit(limit)
    
    cases = list(session.exec(statement).all())
    return cases


@router.get("/{case_id}", response_model=CasePublic)
async def get_case(
    case_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific case by ID
    """
    statement = select(Case).where(Case.id == case_id)
    case = session.exec(statement).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Check access permissions
    if (current_user.role == "clerk" and 
        case.assigned_clerk_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this case"
        )
    
    return case


@router.put("/{case_id}", response_model=CasePublic)
async def update_case(
    case_id: int,
    case_update: CaseUpdate,
    request: Request,
    current_user: User = Depends(require_clerk),
    session: Session = Depends(get_session)
):
    """
    Update a case (Clerk access required)
    """
    statement = select(Case).where(Case.id == case_id)
    case = session.exec(statement).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Check access permissions
    if (current_user.role == "clerk" and 
        case.assigned_clerk_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this case"
        )
    
    # Store original data for audit
    before_data = {
        "title": case.title,
        "synopsis": case.synopsis,
        "status": case.status.value,
        "priority": case.priority.value,
        "estimated_duration_minutes": case.estimated_duration_minutes,
        "assigned_clerk_id": case.assigned_clerk_id,
        "assigned_bench_id": case.assigned_bench_id
    }
    
    # Update fields
    update_data = case_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(case, field, value)
    
    case.updated_at = datetime.utcnow()
    
    session.add(case)
    session.commit()
    session.refresh(case)
    
    # Store updated data for audit
    after_data = {
        "title": case.title,
        "synopsis": case.synopsis,
        "status": case.status.value,
        "priority": case.priority.value,
        "estimated_duration_minutes": case.estimated_duration_minutes,
        "assigned_clerk_id": case.assigned_clerk_id,
        "assigned_bench_id": case.assigned_bench_id
    }
    
    # Log case update
    audit_service.log_case_update(
        session=session,
        user=current_user,
        case_id=case.id,
        before_data=before_data,
        after_data=after_data,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return case


@router.post("/{case_id}/classify")
async def classify_case(
    case_id: int,
    request: Request,
    current_user: User = Depends(require_clerk),
    session: Session = Depends(get_session)
):
    """
    Classify a case using DCM rules engine
    """
    statement = select(Case).where(Case.id == case_id)
    case = session.exec(statement).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Run classification
    classification = dcm_engine.classify_case(case)
    
    # Update case with classification
    case.track = classification.track
    case.track_score = classification.score
    case.track_reasons = str(classification.reasons)  # Store as JSON string
    case.updated_at = datetime.utcnow()
    
    session.add(case)
    session.commit()
    session.refresh(case)
    
    # Log classification
    audit_service.log_case_classification(
        session=session,
        user=current_user,
        case_id=case.id,
        classification_result=classification.dict(),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return {
        "case_id": case.id,
        "classification": classification.dict(),
        "message": f"Case classified as {classification.track.value} track"
    }


@router.post("/{case_id}/override-track")
async def override_case_track(
    case_id: int,
    override_data: CaseOverride,
    request: Request,
    current_user: User = Depends(require_judge),
    session: Session = Depends(get_session)
):
    """
    Override case track classification (Judge access required)
    """
    statement = select(Case).where(Case.id == case_id)
    case = session.exec(statement).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Store original track for audit
    old_track = case.track.value if case.track else None
    
    # Update case with override
    case.track = override_data.new_track
    case.is_track_overridden = True
    case.override_reason = override_data.reason
    case.override_by_user_id = current_user.id
    case.override_at = datetime.utcnow()
    case.updated_at = datetime.utcnow()
    
    session.add(case)
    session.commit()
    session.refresh(case)
    
    # Log track override
    audit_service.log_track_override(
        session=session,
        user=current_user,
        case_id=case.id,
        old_track=old_track or "unclassified",
        new_track=override_data.new_track.value,
        reason=override_data.reason,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return {
        "case_id": case.id,
        "old_track": old_track,
        "new_track": override_data.new_track.value,
        "reason": override_data.reason,
        "overridden_by": current_user.full_name,
        "overridden_at": case.override_at,
        "message": "Case track successfully overridden"
    }


@router.get("/{case_id}/audit-trail")
async def get_case_audit_trail(
    case_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get audit trail for a specific case
    """
    # Verify case exists
    statement = select(Case).where(Case.id == case_id)
    case = session.exec(statement).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Check access permissions
    if (current_user.role == "clerk" and 
        case.assigned_clerk_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this case"
        )
    
    # Get audit trail
    audit_trail = audit_service.get_audit_trail(
        session=session,
        case_id=case_id,
        limit=50
    )
    
    # Get summary
    audit_summary = audit_service.get_case_audit_summary(
        session=session,
        case_id=case_id
    )
    
    return {
        "case_id": case_id,
        "case_number": case.case_number,
        "audit_summary": audit_summary,
        "audit_trail": [
            {
                "id": log.id,
                "action": log.action.value,
                "user_id": log.user_id,
                "description": log.description,
                "created_at": log.created_at,
                "before_data": log.before_data,
                "after_data": log.after_data
            }
            for log in audit_trail
        ]
    }

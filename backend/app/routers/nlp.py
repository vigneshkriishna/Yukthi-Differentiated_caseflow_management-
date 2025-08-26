"""
NLP router for BNS section suggestions and legal assistance
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import get_current_user, require_clerk
from app.models.user import User
from app.models.case import Case
from app.services.nlp import bns_assist, BNSSuggestion
from app.services.audit import audit_service
import json


router = APIRouter()


@router.post("/suggest-laws")
async def suggest_bns_sections(
    case_synopsis: str = Query(..., description="Case synopsis text"),
    max_suggestions: int = Query(5, ge=1, le=10, description="Maximum number of suggestions"),
    request: Request = None,
    current_user: User = Depends(require_clerk),
    session: Session = Depends(get_session)
):
    """
    Suggest BNS sections based on case synopsis (Phase 1 rule-based)
    """
    if len(case_synopsis.strip()) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Case synopsis must be at least 10 characters long"
        )
    
    # Get suggestions using BNS Assist service
    suggestions = bns_assist.suggest_bns_sections(
        case_synopsis=case_synopsis,
        max_suggestions=max_suggestions
    )
    
    # Log NLP suggestion request
    audit_service.log_action(
        session=session,
        action="suggest_laws",
        user=current_user,
        resource_type="nlp_suggestion",
        after_data={
            "synopsis_length": len(case_synopsis),
            "max_suggestions": max_suggestions,
            "suggestions_count": len(suggestions)
        },
        description=f"BNS sections suggested for case synopsis ({len(suggestions)} suggestions)",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return {
        "synopsis": case_synopsis,
        "suggestions": [suggestion.to_dict() for suggestion in suggestions],
        "total_suggestions": len(suggestions),
        "model_version": "1.0.0-rule-based",
        "generated_at": "auto"
    }


@router.post("/suggest-laws-for-case/{case_id}")
async def suggest_laws_for_case(
    case_id: int,
    max_suggestions: int = Query(5, ge=1, le=10),
    update_case: bool = Query(False, description="Whether to update case with suggestions"),
    request: Request = None,
    current_user: User = Depends(require_clerk),
    session: Session = Depends(get_session)
):
    """
    Suggest BNS sections for an existing case
    """
    # Get the case
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
    
    # Get suggestions
    suggestions = bns_assist.suggest_bns_sections(
        case_synopsis=case.synopsis,
        max_suggestions=max_suggestions
    )
    
    # Optionally update the case with suggestions
    if update_case and suggestions:
        suggested_laws_data = [suggestion.to_dict() for suggestion in suggestions]
        case.suggested_laws = json.dumps(suggested_laws_data)
        session.add(case)
        session.commit()
        session.refresh(case)
    
    # Log the suggestion
    audit_service.log_action(
        session=session,
        action="suggest_laws",
        user=current_user,
        resource_type="case",
        resource_id=case_id,
        after_data={
            "suggestions_count": len(suggestions),
            "updated_case": update_case
        },
        description=f"BNS sections suggested for case {case.case_number}",
        case_id=case_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return {
        "case_id": case_id,
        "case_number": case.case_number,
        "synopsis": case.synopsis,
        "suggestions": [suggestion.to_dict() for suggestion in suggestions],
        "total_suggestions": len(suggestions),
        "case_updated": update_case,
        "model_version": "1.0.0-rule-based"
    }


@router.get("/section/{section_number}")
async def get_bns_section_details(
    section_number: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get details for a specific BNS section
    """
    section_details = bns_assist.get_section_details(section_number)
    
    if not section_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"BNS section {section_number} not found"
        )
    
    return section_details


@router.get("/search")
async def search_bns_sections(
    keyword: str = Query(..., min_length=2, description="Keyword to search for"),
    max_results: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user)
):
    """
    Search BNS sections by keyword
    """
    results = bns_assist.search_sections_by_keyword(
        keyword=keyword,
        max_results=max_results
    )
    
    return {
        "keyword": keyword,
        "results": results,
        "total_results": len(results)
    }


@router.get("/statistics")
async def get_nlp_statistics(
    current_user: User = Depends(get_current_user)
):
    """
    Get statistics about the NLP/BNS database
    """
    stats = bns_assist.get_statistics()
    
    return {
        "bns_database": stats,
        "model_info": {
            "current_version": "1.0.0-rule-based",
            "type": "keyword_matching",
            "phase": "1",
            "next_planned": "TF-IDF + Linear SVM baseline"
        }
    }


@router.get("/model-info")
async def get_model_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get information about the current NLP model
    """
    return {
        "model": {
            "name": "BNS Assist v1.0",
            "type": "Rule-based keyword matching",
            "version": "1.0.0",
            "phase": "Phase 1 - Proof of Concept"
        },
        "capabilities": [
            "Keyword-based BNS section suggestion",
            "IPC to BNS mapping (limited)",
            "Section search by keyword",
            "Basic confidence scoring"
        ],
        "limitations": [
            "Rule-based matching only",
            "Limited vocabulary coverage",
            "No context understanding",
            "No machine learning components"
        ],
        "roadmap": {
            "phase_2": "TF-IDF vectorization + Linear SVM",
            "phase_3": "Deep learning models (BERT/RoBERTa)",
            "phase_4": "Multi-lingual support",
            "phase_5": "Case law precedent matching"
        },
        "training_data": {
            "source": "Manually curated keyword mappings",
            "sections_covered": bns_assist.get_statistics()["total_sections"],
            "last_updated": "2024-01-01"
        }
    }


@router.post("/feedback")
async def submit_suggestion_feedback(
    case_id: int,
    section_number: str,
    feedback_type: str = Query(..., regex="^(helpful|not_helpful|incorrect)$"),
    comments: Optional[str] = None,
    request: Request = None,
    current_user: User = Depends(require_clerk),
    session: Session = Depends(get_session)
):
    """
    Submit feedback on BNS section suggestions (for model improvement)
    """
    # Verify case exists and user has access
    statement = select(Case).where(Case.id == case_id)
    case = session.exec(statement).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    if (current_user.role == "clerk" and 
        case.assigned_clerk_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this case"
        )
    
    # Log feedback for future model training
    audit_service.log_action(
        session=session,
        action="nlp_feedback",
        user=current_user,
        resource_type="nlp_feedback",
        after_data={
            "case_id": case_id,
            "section_number": section_number,
            "feedback_type": feedback_type,
            "comments": comments
        },
        description=f"User feedback on BNS suggestion: {feedback_type}",
        case_id=case_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return {
        "message": "Feedback submitted successfully",
        "case_id": case_id,
        "section_number": section_number,
        "feedback_type": feedback_type,
        "note": "Feedback will be used to improve future suggestions"
    }


@router.get("/export/suggestions/{case_id}")
async def export_case_suggestions(
    case_id: int,
    current_user: User = Depends(require_clerk),
    session: Session = Depends(get_session)
):
    """
    Export BNS suggestions for a case (for documentation/legal filing)
    """
    # Get the case
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
    
    # Get current suggestions or generate new ones
    if case.suggested_laws:
        suggestions_data = json.loads(case.suggested_laws)
    else:
        suggestions = bns_assist.suggest_bns_sections(case.synopsis)
        suggestions_data = [s.to_dict() for s in suggestions]
    
    return {
        "case_info": {
            "case_id": case_id,
            "case_number": case.case_number,
            "title": case.title,
            "case_type": case.case_type.value,
            "filing_date": case.filing_date.isoformat()
        },
        "synopsis": case.synopsis,
        "suggested_sections": suggestions_data,
        "export_metadata": {
            "generated_by": current_user.full_name,
            "generated_at": "auto",
            "model_version": "1.0.0-rule-based"
        }
    }

"""
Reports router for analytics and data exports
"""
import csv
import io
import tempfile
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import FileResponse
from sqlmodel import Session, func, select

from app.core.database import get_session
from app.core.security import get_current_user, require_clerk
from app.models.bench import Bench
from app.models.case import Case, CaseStatus, CaseTrack, CaseType
from app.models.hearing import Hearing
from app.models.user import User
from app.services.audit import audit_service

router = APIRouter()


@router.get("/metrics")
async def get_metrics(
    start_date: Optional[date] = Query(None, description="Start date for metrics"),
    end_date: Optional[date] = Query(None, description="End date for metrics"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get analytics summary and metrics
    """
    # Set default date range if not provided (last 30 days)
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Total cases
    total_cases_stmt = select(func.count(Case.id))
    if start_date and end_date:
        total_cases_stmt = total_cases_stmt.where(
            Case.filing_date >= start_date,
            Case.filing_date <= end_date
        )
    total_cases = session.exec(total_cases_stmt).first() or 0

    # Cases by status
    status_counts = {}
    for case_status in CaseStatus:
        count_stmt = select(func.count(Case.id)).where(Case.status == case_status)
        if start_date and end_date:
            count_stmt = count_stmt.where(
                Case.filing_date >= start_date,
                Case.filing_date <= end_date
            )
        count = session.exec(count_stmt).first() or 0
        status_counts[case_status.value] = count

    # Cases by track
    track_counts = {}
    for track in CaseTrack:
        count_stmt = select(func.count(Case.id)).where(Case.track == track)
        if start_date and end_date:
            count_stmt = count_stmt.where(
                Case.filing_date >= start_date,
                Case.filing_date <= end_date
            )
        count = session.exec(count_stmt).first() or 0
        track_counts[track.value] = count

    # Unclassified cases
    unclassified_stmt = select(func.count(Case.id)).where(Case.track.is_(None))
    if start_date and end_date:
        unclassified_stmt = unclassified_stmt.where(
            Case.filing_date >= start_date,
            Case.filing_date <= end_date
        )
    unclassified_cases = session.exec(unclassified_stmt).first() or 0

    # Unplaced cases (filed but not scheduled)
    unplaced_stmt = select(func.count(Case.id)).where(
        Case.status.in_([CaseStatus.FILED, CaseStatus.UNDER_REVIEW])
    )
    if start_date and end_date:
        unplaced_stmt = unplaced_stmt.where(
            Case.filing_date >= start_date,
            Case.filing_date <= end_date
        )
    unplaced_cases = session.exec(unplaced_stmt).first() or 0

    # Average gap days (filing to first hearing) - using simple calculation
    avg_gap_days = 7.5  # Placeholder for actual calculation

    # Workload distribution (cases per bench)
    bench_workload = {}
    bench_stmt = select(Bench)
    benches = list(session.exec(bench_stmt).all())

    for bench in benches:
        # Count hearings for this bench in date range
        hearing_count_stmt = select(func.count(Hearing.id)).where(
            Hearing.bench_id == bench.id,
            Hearing.hearing_date >= start_date,
            Hearing.hearing_date <= end_date
        )
        hearing_count = session.exec(hearing_count_stmt).first() or 0
        bench_workload[bench.name] = hearing_count

    # Recent activity (last 7 days)
    recent_date = date.today() - timedelta(days=7)
    recent_cases_stmt = select(func.count(Case.id)).where(
        Case.created_at >= datetime.combine(recent_date, datetime.min.time())
    )
    recent_cases = session.exec(recent_cases_stmt).first() or 0

    recent_hearings_stmt = select(func.count(Hearing.id)).where(
        Hearing.hearing_date >= recent_date
    )
    recent_hearings = session.exec(recent_hearings_stmt).first() or 0

    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "summary": {
            "total_cases": total_cases,
            "unclassified_cases": unclassified_cases,
            "unplaced_cases": unplaced_cases,
            "unplaced_percentage": round((unplaced_cases / total_cases) * 100, 1) if total_cases > 0 else 0,
            "average_gap_days": round(avg_gap_days, 1)
        },
        "distribution": {
            "by_status": status_counts,
            "by_track": track_counts,
            "workload_by_bench": bench_workload
        },
        "recent_activity": {
            "new_cases_last_7_days": recent_cases,
            "hearings_last_7_days": recent_hearings
        },
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/case-statistics")
async def get_case_statistics(
    case_type: Optional[CaseType] = None,
    track: Optional[CaseTrack] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get detailed case statistics with optional filtering
    """
    base_stmt = select(Case)

    # Apply filters
    if case_type:
        base_stmt = base_stmt.where(Case.case_type == case_type)
    if track:
        base_stmt = base_stmt.where(Case.track == track)

    cases = list(session.exec(base_stmt).all())

    if not cases:
        return {
            "total_cases": 0,
            "statistics": {},
            "message": "No cases found matching the criteria"
        }

    # Calculate statistics
    total_cases = len(cases)
    total_duration = sum(case.estimated_duration_minutes for case in cases)
    avg_duration = total_duration / total_cases if total_cases > 0 else 0

    # Age distribution
    today = date.today()
    age_buckets = {
        "0-30_days": 0,
        "31-90_days": 0,
        "91-180_days": 0,
        "180+_days": 0
    }

    for case in cases:
        age_days = (today - case.filing_date).days
        if age_days <= 30:
            age_buckets["0-30_days"] += 1
        elif age_days <= 90:
            age_buckets["31-90_days"] += 1
        elif age_days <= 180:
            age_buckets["91-180_days"] += 1
        else:
            age_buckets["180+_days"] += 1

    # Track override statistics
    overridden_cases = [case for case in cases if case.is_track_overridden]
    override_rate = (len(overridden_cases) / total_cases) * 100 if total_cases > 0 else 0

    return {
        "filters": {
            "case_type": case_type.value if case_type else "all",
            "track": track.value if track else "all"
        },
        "total_cases": total_cases,
        "statistics": {
            "duration": {
                "total_minutes": total_duration,
                "average_minutes": round(avg_duration, 1),
                "total_hours": round(total_duration / 60, 1)
            },
            "age_distribution": age_buckets,
            "track_overrides": {
                "total_overrides": len(overridden_cases),
                "override_rate_percentage": round(override_rate, 1)
            }
        }
    }


@router.get("/export/cause-list")
async def export_cause_list(
    date: date = Query(..., description="Date for cause list"),
    format: str = Query("csv", regex="^(csv|pdf)$", description="Export format"),
    request: Request = None,
    current_user: User = Depends(require_clerk),
    session: Session = Depends(get_session)
):
    """
    Export cause list as CSV or PDF
    """
    # Get hearings for the date
    stmt = select(Hearing).where(Hearing.hearing_date == date)
    stmt = stmt.order_by(Hearing.bench_id, Hearing.start_time)
    hearings = list(session.exec(stmt).all())

    if not hearings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hearings found for {date}"
        )

    # Prepare data
    cause_list_data = []
    for hearing in hearings:
        # Get case info
        case_stmt = select(Case).where(Case.id == hearing.case_id)
        case = session.exec(case_stmt).first()

        # Get bench info
        bench_stmt = select(Bench).where(Bench.id == hearing.bench_id)
        bench = session.exec(bench_stmt).first()

        # Get judge info
        judge_stmt = select(User).where(User.id == hearing.judge_id)
        judge = session.exec(judge_stmt).first()

        cause_list_data.append({
            "Sr. No.": len(cause_list_data) + 1,
            "Case Number": case.case_number if case else "Unknown",
            "Case Title": case.title if case else "Unknown",
            "Case Type": case.case_type.value if case else "Unknown",
            "Track": case.track.value if case and case.track else "Unclassified",
            "Start Time": hearing.start_time.strftime("%H:%M"),
            "Duration (min)": hearing.estimated_duration_minutes,
            "Bench": bench.name if bench else f"Bench {hearing.bench_id}",
            "Court Number": bench.court_number if bench else "Unknown",
            "Judge": judge.full_name if judge else "Unknown",
            "Status": hearing.status.value,
            "Notes": hearing.notes or ""
        })

    # Log report generation
    audit_service.log_report_generation(
        session=session,
        user=current_user,
        report_type=f"cause_list_{format}",
        report_params={"date": date.isoformat(), "format": format},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    if format == "csv":
        return _export_csv(cause_list_data, f"cause_list_{date.isoformat()}")
    else:  # pdf
        return _export_pdf(cause_list_data, f"Cause List - {date.strftime('%B %d, %Y')}")


def _export_csv(data: List[Dict[str, Any]], filename: str) -> Response:
    """Export data as CSV"""
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data to export"
        )

    # Create CSV content
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

    # Create response
    csv_content = output.getvalue()
    output.close()

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}.csv"}
    )


def _export_pdf(data: List[Dict[str, Any]], title: str) -> FileResponse:
    """Export data as PDF (simplified version)"""
    # For now, return a placeholder
    # In a real implementation, you would use ReportLab to generate PDF

    # Create a temporary text file as placeholder
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_file.write(f"{title}\n")
        temp_file.write("=" * len(title) + "\n\n")

        for item in data:
            for key, value in item.items():
                temp_file.write(f"{key}: {value}\n")
            temp_file.write("\n")

        temp_file_path = temp_file.name

    return FileResponse(
        path=temp_file_path,
        filename=f"{title.replace(' ', '_').lower()}.txt",
        media_type="text/plain"
    )


@router.get("/dashboard")
async def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get dashboard data tailored to user role
    """
    dashboard_data = {
        "user": {
            "id": current_user.id,
            "name": current_user.full_name,
            "role": current_user.role.value
        },
        "quick_stats": {},
        "recent_activity": {},
        "upcoming": {}
    }

    if current_user.role in ["clerk", "admin"]:
        # Clerk dashboard

        # Cases assigned to this clerk
        my_cases_stmt = select(func.count(Case.id)).where(
            Case.assigned_clerk_id == current_user.id
        )
        my_cases = session.exec(my_cases_stmt).first() or 0

        # Unclassified cases assigned to me
        unclassified_stmt = select(func.count(Case.id)).where(
            Case.assigned_clerk_id == current_user.id,
            Case.track.is_(None)
        )
        unclassified = session.exec(unclassified_stmt).first() or 0

        dashboard_data["quick_stats"] = {
            "my_cases": my_cases,
            "unclassified_cases": unclassified,
            "classification_rate": round(((my_cases - unclassified) / my_cases) * 100, 1) if my_cases > 0 else 0
        }

    elif current_user.role == "judge":
        # Judge dashboard

        # Today's hearings
        today = date.today()
        today_hearings_stmt = select(func.count(Hearing.id)).where(
            Hearing.judge_id == current_user.id,
            Hearing.hearing_date == today
        )
        today_hearings = session.exec(today_hearings_stmt).first() or 0

        # This week's hearings
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        week_hearings_stmt = select(func.count(Hearing.id)).where(
            Hearing.judge_id == current_user.id,
            Hearing.hearing_date >= week_start,
            Hearing.hearing_date <= week_end
        )
        week_hearings = session.exec(week_hearings_stmt).first() or 0

        dashboard_data["quick_stats"] = {
            "today_hearings": today_hearings,
            "week_hearings": week_hearings
        }

        # Upcoming hearings
        upcoming_stmt = select(Hearing).where(
            Hearing.judge_id == current_user.id,
            Hearing.hearing_date >= today
        ).order_by(Hearing.hearing_date, Hearing.start_time).limit(5)

        upcoming_hearings = list(session.exec(upcoming_stmt).all())
        dashboard_data["upcoming"]["hearings"] = [
            {
                "hearing_id": h.id,
                "date": h.hearing_date.isoformat(),
                "time": h.start_time.strftime("%H:%M"),
                "case_id": h.case_id
            }
            for h in upcoming_hearings
        ]

    return dashboard_data

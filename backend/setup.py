#!/usr/bin/env python3
"""
Startup script for DCM System Backend
Creates initial data and starts the server
"""
import asyncio
import sys
from datetime import date, datetime
from sqlmodel import Session, select
from app.core.database import create_db_and_tables, engine
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.bench import Bench
from app.models.case import Case, CaseType, CasePriority, CaseStatus


def create_initial_data():
    """Create initial data for development"""
    print("Creating initial data...")
    
    with Session(engine) as session:
        # Check if data already exists
        existing_user = session.exec(select(User)).first()
        if existing_user:
            print("Initial data already exists, skipping...")
            return
        
        # Create initial users
        users = [
            User(
                username="admin",
                email="admin@dcm.gov.in",
                full_name="System Administrator",
                role=UserRole.ADMIN,
                hashed_password=get_password_hash("admin123"),
                is_active=True
            ),
            User(
                username="judge1",
                email="judge1@court.gov.in", 
                full_name="Justice A.K. Sharma",
                role=UserRole.JUDGE,
                hashed_password=get_password_hash("judge123"),
                is_active=True
            ),
            User(
                username="clerk1",
                email="clerk1@court.gov.in",
                full_name="Rajesh Kumar",
                role=UserRole.CLERK,
                hashed_password=get_password_hash("clerk123"),
                is_active=True
            ),
            User(
                username="lawyer1",
                email="lawyer1@bar.org.in",
                full_name="Advocate Priya Singh",
                role=UserRole.LAWYER,
                hashed_password=get_password_hash("lawyer123"),
                is_active=True
            )
        ]
        
        for user in users:
            session.add(user)
        
        # Create initial benches
        benches = [
            Bench(
                name="Court No. 1",
                court_number="1",
                capacity=50,
                is_active=True
            ),
            Bench(
                name="Court No. 2", 
                court_number="2",
                capacity=45,
                is_active=True
            ),
            Bench(
                name="Fast Track Court",
                court_number="FTC-1",
                capacity=60,
                is_active=True
            )
        ]
        
        for bench in benches:
            session.add(bench)
        
        session.commit()
        session.refresh(users[2])  # Get clerk ID
        
        # Create sample cases
        sample_cases = [
            Case(
                case_number="CR/2024/001",
                title="State vs. Ramesh Kumar",
                case_type=CaseType.CRIMINAL,
                synopsis="The accused committed theft of a mobile phone worth Rs. 25,000 from the complainant's residence",
                filing_date=date.today(),
                status=CaseStatus.FILED,
                priority=CasePriority.MEDIUM,
                estimated_duration_minutes=120,
                assigned_clerk_id=users[2].id
            ),
            Case(
                case_number="CIV/2024/002",
                title="ABC Ltd vs. XYZ Corp",
                case_type=CaseType.COMMERCIAL,
                synopsis="Commercial dispute regarding breach of contract for supply of goods worth Rs. 10 lakhs",
                filing_date=date.today(),
                status=CaseStatus.FILED,
                priority=CasePriority.HIGH,
                estimated_duration_minutes=240,
                assigned_clerk_id=users[2].id
            ),
            Case(
                case_number="CR/2024/003",
                title="State vs. Unknown",
                case_type=CaseType.CRIMINAL,
                synopsis="Simple traffic violation case - running red light, fine amount Rs. 500",
                filing_date=date.today(),
                status=CaseStatus.FILED,
                priority=CasePriority.LOW,
                estimated_duration_minutes=30,
                assigned_clerk_id=users[2].id
            )
        ]
        
        for case in sample_cases:
            session.add(case)
        
        session.commit()
        
        print("✅ Initial data created successfully!")
        print("\nDefault login credentials:")
        print("Admin: admin / admin123")
        print("Judge: judge1 / judge123") 
        print("Clerk: clerk1 / clerk123")
        print("Lawyer: lawyer1 / lawyer123")


def main():
    """Main startup function"""
    print("🏛️  DCM System Backend Startup")
    print("=" * 40)
    
    # Create database tables
    print("Creating database tables...")
    create_db_and_tables()
    print("✅ Database tables created!")
    
    # Create initial data
    create_initial_data()
    
    print("\n🚀 Backend is ready!")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("\nTo start the server:")
    print("uvicorn main:app --reload")


if __name__ == "__main__":
    main()

"""
Quick data seeding for smart scheduling system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, date, time
from app.core.database import get_session
from app.models.bench import Bench
from app.models.user import User, UserRole
from app.models.case import Case, CaseType, CaseStatus, CasePriority
from sqlmodel import Session

def seed_basic_data():
    print("🌱 Seeding Basic Data for Smart Scheduling")
    print("=" * 50)
    
    session = next(get_session())
    
    try:
        # Create benches
        print("\n1. Creating Benches...")
        benches = [
            Bench(name="Civil Bench 1", court_number="C1", is_active=True),
            Bench(name="Criminal Bench 1", court_number="CR1", is_active=True),
            Bench(name="Commercial Bench 1", court_number="CM1", is_active=True),
        ]
        
        for bench in benches:
            session.add(bench)
        session.commit()
        print(f"   ✅ Created {len(benches)} benches")
        
        # Create a judge user if not exists
        print("\n2. Creating Judge User...")
        existing_judge = session.query(User).filter(User.role == UserRole.JUDGE).first()
        if not existing_judge:
            judge = User(
                username="judge1",
                email="judge1@dcm.com",
                full_name="Judge Smith",
                role=UserRole.JUDGE,
                is_active=True,
                hashed_password="$2b$12$dummy_hash"  # Dummy hash for testing
            )
            session.add(judge)
            session.commit()
            print("   ✅ Created judge user")
        else:
            print("   ✅ Judge user already exists")
        
        # Create some sample cases if none exist
        print("\n3. Creating Sample Cases...")
        existing_cases = session.query(Case).count()
        if existing_cases < 5:
            sample_cases = [
                Case(
                    case_number="CIVIL/2024/001",
                    case_title="Property Dispute Case",
                    case_type=CaseType.CIVIL,
                    priority=CasePriority.MEDIUM,
                    status=CaseStatus.FILED,
                    filing_date=date.today(),
                    description="Property boundary dispute between neighbors"
                ),
                Case(
                    case_number="CRIMINAL/2024/001", 
                    case_title="Theft Case",
                    case_type=CaseType.CRIMINAL,
                    priority=CasePriority.URGENT,
                    status=CaseStatus.UNDER_REVIEW,
                    filing_date=date.today(),
                    description="Theft of electronic goods"
                ),
                Case(
                    case_number="CIVIL/2024/002",
                    case_title="Contract Dispute",
                    case_type=CaseType.CIVIL,
                    priority=CasePriority.HIGH,
                    status=CaseStatus.FILED,
                    filing_date=date.today(),
                    description="Breach of service contract"
                )
            ]
            
            for case in sample_cases:
                session.add(case)
            session.commit()
            print(f"   ✅ Created {len(sample_cases)} sample cases")
        else:
            print(f"   ✅ {existing_cases} cases already exist")
        
        print("\n" + "=" * 50)
        print("✅ Basic data seeding completed!")
        
    except Exception as e:
        print(f"   ❌ Error during seeding: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    seed_basic_data()
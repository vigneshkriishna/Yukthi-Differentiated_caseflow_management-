"""
Demo data seeder for DCM System
Creates realistic test data for demonstrations
"""
import random
import json
from datetime import date, datetime, timedelta
from faker import Faker
from sqlmodel import Session, select
from app.core.database import create_db_and_tables, engine
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.bench import Bench
from app.models.case import Case, CaseType, CasePriority, CaseStatus, CaseTrack
from app.models.hearing import Hearing, HearingStatus

fake = Faker('en_IN')  # Indian locale for realistic names
random.seed(42)  # Deterministic for consistent demos


class DemoDataSeeder:
    def __init__(self):
        self.users = {}
        self.benches = {}
        self.cases = []
        
    def create_users(self, session: Session):
        """Create demo users"""
        print("Creating demo users...")
        
        users_data = [
            ("admin", "admin@dcm.gov.in", "System Administrator", UserRole.ADMIN),
            ("chief_judge", "chief.judge@court.gov.in", "Justice Dr. A.K. Sharma", UserRole.JUDGE),
            ("judge_criminal", "judge.criminal@court.gov.in", "Justice Ms. Priya Patel", UserRole.JUDGE),
            ("judge_civil", "judge.civil@court.gov.in", "Justice Mr. R.K. Verma", UserRole.JUDGE),
            ("senior_clerk", "senior.clerk@court.gov.in", "Mr. Rajesh Kumar Singh", UserRole.CLERK),
            ("clerk_criminal", "clerk.criminal@court.gov.in", "Ms. Sunita Sharma", UserRole.CLERK),
            ("clerk_civil", "clerk.civil@court.gov.in", "Mr. Anil Gupta", UserRole.CLERK),
            ("advocate_sr", "advocate.sr@bar.org.in", "Advocate Vikram Singh", UserRole.LAWYER),
            ("advocate_jr", "advocate.jr@bar.org.in", "Advocate Neha Agarwal", UserRole.LAWYER),
            ("public_user", "public@citizen.gov.in", "Ms. Asha Devi", UserRole.PUBLIC),
        ]
        
        for username, email, full_name, role in users_data:
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                role=role,
                hashed_password=get_password_hash("demo123"),
                is_active=True,
                created_at=datetime.utcnow()
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            self.users[username] = user
            
        print(f"✅ Created {len(users_data)} demo users")
        
    def create_benches(self, session: Session):
        """Create demo court benches"""
        print("Creating demo benches...")
        
        benches_data = [
            ("Chief Justice Court", "CJ-1", 60),
            ("Criminal Court No. 1", "CR-1", 50),
            ("Criminal Court No. 2", "CR-2", 45),
            ("Civil Court No. 1", "CV-1", 40),
            ("Civil Court No. 2", "CV-2", 40),
            ("Commercial Court", "COM-1", 35),
            ("Family Court", "FAM-1", 30),
            ("Fast Track Court - 1", "FTC-1", 70),
            ("Fast Track Court - 2", "FTC-2", 65),
        ]
        
        for name, court_number, capacity in benches_data:
            bench = Bench(
                name=name,
                court_number=court_number,
                capacity=capacity,
                is_active=True,
                created_at=datetime.utcnow()
            )
            session.add(bench)
            session.commit()
            session.refresh(bench)
            self.benches[court_number] = bench
            
        print(f"✅ Created {len(benches_data)} demo benches")
        
    def generate_case_synopsis(self, case_type: CaseType, keywords: list) -> str:
        """Generate realistic case synopsis"""
        
        case_templates = {
            CaseType.CRIMINAL: [
                "The accused {} committed {} against the complainant {} on {}. The incident occurred at {} and involved {}. The complainant filed an FIR at {} police station.",
                "A case of {} was reported where the accused {} allegedly {} the victim {}. The incident happened on {} at {} in the presence of witnesses.",
                "The accused {} is charged with {} under various sections. The incident occurred on {} when {} happened at {}."
            ],
            CaseType.CIVIL: [
                "A civil dispute between {} and {} regarding {}. The matter pertains to {} and involves a claim of Rs. {} lakhs. The dispute arose on {}.",
                "The plaintiff {} seeks relief against defendant {} for {}. The case involves {} and damages worth Rs. {} lakhs are claimed.",
                "A property dispute between {} and {} over {}. The matter involves {} and requires urgent judicial intervention."
            ],
            CaseType.COMMERCIAL: [
                "A commercial dispute between {} Ltd. and {} Corp. regarding {}. The contract worth Rs. {} crores was breached on {}. The matter involves {}.",
                "The plaintiff company {} filed a suit against {} for breach of contract. The agreement involved {} worth Rs. {} crores signed on {}.",
                "A business dispute over {} between {} and {}. The transaction worth Rs. {} crores is disputed due to {}."
            ],
            CaseType.FAMILY: [
                "A matrimonial dispute between {} and {} regarding {}. The couple married on {} and have {} children. The issue pertains to {}.",
                "A family matter involving {} and {} over {}. The dispute arose regarding {} and affects the welfare of {}.",
                "A maintenance case filed by {} against {} for {}. The marriage took place on {} and the issues relate to {}."
            ]
        }
        
        templates = case_templates.get(case_type, case_templates[CaseType.CRIMINAL])
        template = random.choice(templates)
        
        # Generate random details based on case type
        if case_type == CaseType.CRIMINAL:
            accused = fake.name()
            victim = fake.name()
            crime = random.choice(keywords)
            location = fake.city()
            date_str = fake.date_between(start_date='-30d', end_date='today').strftime('%d/%m/%Y')
            police_station = fake.city() + " Police Station"
            return template.format(accused, crime, victim, date_str, location, crime, police_station)
            
        elif case_type == CaseType.CIVIL:
            plaintiff = fake.name()
            defendant = fake.name()
            matter = random.choice(keywords)
            amount = random.randint(5, 500)
            date_str = fake.date_between(start_date='-90d', end_date='today').strftime('%d/%m/%Y')
            return template.format(plaintiff, defendant, matter, matter, amount, date_str)
            
        elif case_type == CaseType.COMMERCIAL:
            company1 = fake.company()
            company2 = fake.company()
            matter = random.choice(keywords)
            amount = random.randint(10, 1000)
            date_str = fake.date_between(start_date='-180d', end_date='today').strftime('%d/%m/%Y')
            return template.format(company1, company2, matter, amount, date_str, matter)
            
        else:  # FAMILY
            person1 = fake.name()
            person2 = fake.name()
            matter = random.choice(keywords)
            date_str = fake.date_between(start_date='-2000d', end_date='-365d').strftime('%d/%m/%Y')
            children = random.choice(["no", "one", "two", "three"])
            return template.format(person1, person2, matter, date_str, children, matter)
    
    def create_cases(self, session: Session, count: int = 150):
        """Create demo cases with realistic data"""
        print(f"Creating {count} demo cases...")
        
        # Define keywords for different case types
        case_keywords = {
            CaseType.CRIMINAL: [
                "theft of mobile phone", "burglary", "assault", "fraud", "cheating",
                "robbery", "murder", "kidnapping", "drug possession", "traffic violation",
                "domestic violence", "cybercrime", "forgery", "extortion", "bribery"
            ],
            CaseType.CIVIL: [
                "property dispute", "contract breach", "defamation", "negligence",
                "land acquisition", "inheritance dispute", "boundary dispute",
                "rent agreement", "loan recovery", "insurance claim"
            ],
            CaseType.COMMERCIAL: [
                "breach of contract", "partnership dispute", "trademark infringement",
                "corporate governance", "merger dispute", "supply chain breach",
                "licensing agreement", "joint venture", "franchise dispute",
                "intellectual property"
            ],
            CaseType.FAMILY: [
                "divorce proceedings", "child custody", "maintenance", "domestic violence",
                "adoption", "property settlement", "alimony", "guardianship",
                "marriage disputes", "inheritance rights"
            ],
            CaseType.CONSTITUTIONAL: [
                "fundamental rights violation", "constitutional validity", "writ petition",
                "public interest litigation", "judicial review", "separation of powers",
                "constitutional interpretation", "constitutional amendment challenge",
                "federalism dispute", "constitutional remedy"
            ]
        }
        
        clerk_users = [user for user in self.users.values() if user.role == UserRole.CLERK]
        
        for i in range(count):
            case_type = random.choice(list(CaseType))
            keywords = case_keywords[case_type]
            
            # Generate case number
            year = random.choice([2023, 2024])
            case_number = f"{case_type.value.upper()[:3]}/{year}/{i+1:04d}"
            
            # Generate case title
            if case_type == CaseType.CRIMINAL:
                title = f"State vs. {fake.name()}"
            else:
                title = f"{fake.name()} vs. {fake.name()}"
            
            # Generate synopsis
            synopsis = self.generate_case_synopsis(case_type, keywords)
            
            # Random filing date (last 6 months)
            filing_date = fake.date_between(start_date='-180d', end_date='today')
            
            # Assign priority and duration based on case type and keywords
            if any(kw in synopsis.lower() for kw in ["murder", "rape", "serious", "urgent"]):
                priority = CasePriority.URGENT
                duration = random.randint(180, 360)
            elif any(kw in synopsis.lower() for kw in ["fraud", "robbery", "commercial"]):
                priority = CasePriority.HIGH
                duration = random.randint(120, 240)
            elif any(kw in synopsis.lower() for kw in ["traffic", "simple", "minor"]):
                priority = CasePriority.LOW
                duration = random.randint(30, 90)
            else:
                priority = CasePriority.MEDIUM
                duration = random.randint(60, 150)
            
            # Random status distribution
            status_weights = [
                (CaseStatus.FILED, 0.4),
                (CaseStatus.UNDER_REVIEW, 0.3),
                (CaseStatus.SCHEDULED, 0.2),
                (CaseStatus.HEARING, 0.05),
                (CaseStatus.DISPOSED, 0.05)
            ]
            status = random.choices(
                [s[0] for s in status_weights],
                weights=[s[1] for s in status_weights]
            )[0]
            
            case = Case(
                case_number=case_number,
                title=title,
                case_type=case_type,
                synopsis=synopsis,
                filing_date=filing_date,
                status=status,
                priority=priority,
                estimated_duration_minutes=duration,
                assigned_clerk_id=random.choice(clerk_users).id,
                created_at=datetime.combine(filing_date, datetime.min.time())
            )
            
            session.add(case)
            
            # Occasionally add some pre-classified cases
            if random.random() < 0.3:  # 30% pre-classified
                if duration <= 90:
                    case.track = CaseTrack.FAST
                elif duration >= 180:
                    case.track = CaseTrack.COMPLEX
                else:
                    case.track = CaseTrack.REGULAR
                case.track_score = round(random.uniform(-3, 5), 2)
                case.track_reasons = json.dumps([f"Auto-classified based on {random.choice(['duration', 'keywords', 'case type'])}"])
        
        session.commit()
        
        # Get all created cases
        cases_stmt = select(Case)
        self.cases = list(session.exec(cases_stmt).all())
        
        print(f"✅ Created {len(self.cases)} demo cases")
        
    def create_some_hearings(self, session: Session):
        """Create some demo hearings"""
        print("Creating demo hearings...")
        
        # Create hearings for some scheduled cases
        scheduled_cases = [case for case in self.cases if case.status == CaseStatus.SCHEDULED]
        judge_users = [user for user in self.users.values() if user.role == UserRole.JUDGE]
        bench_list = list(self.benches.values())
        
        hearings_created = 0
        for case in scheduled_cases[:20]:  # Limit to 20 hearings
            # Random hearing date (next 30 days)
            hearing_date = fake.date_between(start_date='today', end_date='+30d')
            
            # Random time between 10 AM and 4 PM
            start_hour = random.randint(10, 15)
            start_minute = random.choice([0, 30])
            start_time = datetime.strptime(f"{start_hour}:{start_minute:02d}", "%H:%M").time()
            
            hearing = Hearing(
                case_id=case.id,
                judge_id=random.choice(judge_users).id,
                bench_id=random.choice(bench_list).id,
                hearing_date=hearing_date,
                start_time=start_time,
                estimated_duration_minutes=case.estimated_duration_minutes,
                status=HearingStatus.SCHEDULED,
                notes=f"Demo hearing for {case.case_number}",
                created_at=datetime.utcnow()
            )
            
            session.add(hearing)
            hearings_created += 1
            
        session.commit()
        print(f"✅ Created {hearings_created} demo hearings")
        
    def print_summary(self):
        """Print seeding summary"""
        print("\n" + "="*60)
        print("🏛️ DEMO DATA SEEDING COMPLETE")
        print("="*60)
        print(f"👥 Users: {len(self.users)} (Admin/Judges/Clerks/Lawyers/Public)")
        print(f"⚖️ Benches: {len(self.benches)} (Various court types)")
        print(f"📁 Cases: {len(self.cases)} (Mixed types and priorities)")
        print(f"🗓️ Hearings: Demo hearings scheduled")
        print("\n🔑 Login Credentials (all passwords: demo123):")
        for username, user in self.users.items():
            print(f"  • {username} ({user.role.value}): {username} / demo123")
        
        print("\n📊 Case Distribution:")
        case_types = {}
        case_tracks = {}
        case_statuses = {}
        
        for case in self.cases:
            case_types[case.case_type.value] = case_types.get(case.case_type.value, 0) + 1
            case_statuses[case.status.value] = case_statuses.get(case.status.value, 0) + 1
            if case.track:
                case_tracks[case.track.value] = case_tracks.get(case.track.value, 0) + 1
        
        print("  By Type:", dict(sorted(case_types.items())))
        print("  By Status:", dict(sorted(case_statuses.items())))
        print("  By Track:", dict(sorted(case_tracks.items())))
        
        print("\n🚀 Ready for demo! Start the server:")
        print("  uvicorn main:app --reload")
        print("  API Docs: http://localhost:8000/docs")


def main():
    """Main seeding function"""
    print("🌱 Starting Demo Data Seeding...")
    
    # Create database tables
    create_db_and_tables()
    
    with Session(engine) as session:
        # Check if data already exists
        existing_users = session.exec(select(User)).first()
        if existing_users:
            print("⚠️ Demo data already exists. Skipping seeding.")
            print("Drop the database to reseed fresh data.")
            return
        
        seeder = DemoDataSeeder()
        
        # Seed all data
        seeder.create_users(session)
        seeder.create_benches(session)
        seeder.create_cases(session, count=150)
        seeder.create_some_hearings(session)
        
        # Print summary
        seeder.print_summary()


if __name__ == "__main__":
    main()

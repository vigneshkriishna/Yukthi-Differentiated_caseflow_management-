"""
Generate Large Dataset (100+ Cases) for DCM System
Realistic Indian legal cases with BNS sections, priorities, and case types
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, date, timedelta
import random
from pymongo import MongoClient
from app.models.case import CaseType, CaseStatus, CasePriority, CaseTrack
from app.models.user import UserRole

# Use proper config
try:
    from config import Config
    config = Config()
    MONGO_URI = config.MONGODB_URL
    DB_NAME = config.DATABASE_NAME
except:
    # Fallback
    MONGO_URI = "mongodb+srv://vigneshpop:ABhQx4ap6qtrP1ed@cluster0.w7x5vdv.mongodb.net/"
    DB_NAME = "dcm_system"

# Realistic case templates
CRIMINAL_CASES = [
    {
        "title": "Theft of Mobile Phone",
        "description": "Complainant reported theft of iPhone 14 Pro from pocket during crowded market visit. CCTV footage shows suspect.",
        "bns_section": "Section 303(2) - Theft",
        "keywords": ["theft", "mobile phone", "market", "CCTV"]
    },
    {
        "title": "Assault and Battery Case",
        "description": "Victim sustained injuries after altercation at restaurant. Medical reports confirm grievous hurt. Multiple witnesses present.",
        "bns_section": "Section 115 - Voluntarily Causing Hurt",
        "keywords": ["assault", "battery", "grievous hurt", "witnesses"]
    },
    {
        "title": "Cheating and Forgery",
        "description": "Accused created fake documents to obtain loan of Rs 5 lakhs from complainant. Forged signatures verified by expert.",
        "bns_section": "Section 316 - Cheating",
        "keywords": ["cheating", "forgery", "fake documents", "loan fraud"]
    },
    {
        "title": "Robbery at Gunpoint",
        "description": "Armed robbery at jewelry shop in broad daylight. Three suspects fled with gold worth Rs 15 lakhs. Gun recovered.",
        "bns_section": "Section 309 - Robbery",
        "keywords": ["robbery", "armed", "jewelry", "gun"]
    },
    {
        "title": "Sexual Harassment at Workplace",
        "description": "Female employee filed complaint against supervisor for unwanted advances and inappropriate comments over 6 months.",
        "bns_section": "Section 354 - Sexual Harassment",
        "keywords": ["sexual harassment", "workplace", "inappropriate conduct"]
    },
    {
        "title": "Drunk Driving Accident",
        "description": "Accused driving under influence caused collision resulting in serious injuries to two pedestrians. Blood alcohol level 0.15%.",
        "bns_section": "Section 281 - Rash Driving",
        "keywords": ["drunk driving", "accident", "rash driving", "injuries"]
    },
    {
        "title": "Kidnapping of Minor",
        "description": "8-year-old child abducted from school premises. Ransom demand of Rs 10 lakhs made. Child recovered safely within 24 hours.",
        "bns_section": "Section 137 - Kidnapping",
        "keywords": ["kidnapping", "minor", "ransom", "abduction"]
    },
    {
        "title": "Drug Possession and Sale",
        "description": "Police raid recovered 500 grams of heroin and Rs 2 lakhs cash. Accused admitted to regular drug peddling activities.",
        "bns_section": "NDPS Act Section 21",
        "keywords": ["drugs", "heroin", "possession", "peddling"]
    },
    {
        "title": "Domestic Violence Case",
        "description": "Wife filed complaint against husband for repeated physical and mental abuse. Medical evidence of injuries submitted.",
        "bns_section": "Section 498A - Cruelty by Husband",
        "keywords": ["domestic violence", "cruelty", "abuse", "matrimonial"]
    },
    {
        "title": "Cyber Fraud - Phishing",
        "description": "Victim lost Rs 3 lakhs through phishing email. Accused accessed bank account using stolen credentials.",
        "bns_section": "IT Act Section 66C - Identity Theft",
        "keywords": ["cyber fraud", "phishing", "identity theft", "online banking"]
    },
    {
        "title": "Murder Investigation",
        "description": "Body discovered with multiple stab wounds. Prime suspect arrested based on forensic evidence and motive established.",
        "bns_section": "Section 103 - Murder",
        "keywords": ["murder", "homicide", "forensic", "investigation"]
    },
    {
        "title": "Bribery Case - Public Servant",
        "description": "Government official caught accepting Rs 50,000 bribe in sting operation. Audio-video evidence available.",
        "bns_section": "Prevention of Corruption Act",
        "keywords": ["bribery", "corruption", "public servant", "sting"]
    },
]

CIVIL_CASES = [
    {
        "title": "Property Boundary Dispute",
        "description": "Neighbors disputing 2-foot strip of land between properties. Survey reports contradict each other.",
        "legal_issue": "Property Rights",
        "keywords": ["property", "boundary", "land dispute", "survey"]
    },
    {
        "title": "Contract Breach - Construction",
        "description": "Builder failed to deliver apartment on promised date. Delay of 18 months. Buyer seeking compensation.",
        "legal_issue": "Contract Law",
        "keywords": ["contract breach", "construction", "delay", "compensation"]
    },
    {
        "title": "Defamation Suit",
        "description": "Plaintiff alleges defendant published false statements damaging professional reputation. Claiming Rs 25 lakhs damages.",
        "legal_issue": "Defamation",
        "keywords": ["defamation", "libel", "reputation", "damages"]
    },
    {
        "title": "Tenant Eviction Case",
        "description": "Landlord seeking eviction of tenant for non-payment of rent for 8 months and property damage.",
        "legal_issue": "Rent Control",
        "keywords": ["eviction", "tenant", "rent", "landlord"]
    },
    {
        "title": "Inheritance Dispute",
        "description": "Three siblings contesting father's will. Allegations of undue influence and mental incapacity at time of execution.",
        "legal_issue": "Succession",
        "keywords": ["inheritance", "will", "succession", "property"]
    },
    {
        "title": "Partnership Dissolution",
        "description": "Business partners seeking dissolution after 10 years. Dispute over profit sharing and asset division.",
        "legal_issue": "Partnership Act",
        "keywords": ["partnership", "dissolution", "business dispute", "profits"]
    },
    {
        "title": "Medical Negligence",
        "description": "Patient suffered complications after surgery due to alleged negligent treatment. Seeking Rs 50 lakhs compensation.",
        "legal_issue": "Tort - Negligence",
        "keywords": ["medical negligence", "malpractice", "compensation", "hospital"]
    },
    {
        "title": "Consumer Complaint - Defective Product",
        "description": "Customer purchased defective refrigerator. Company refusing replacement or refund despite warranty.",
        "legal_issue": "Consumer Protection",
        "keywords": ["consumer complaint", "defective product", "warranty", "refund"]
    },
]

FAMILY_CASES = [
    {
        "title": "Divorce - Mutual Consent",
        "description": "Couple married for 7 years seeking divorce by mutual consent. All terms agreed including child custody.",
        "legal_issue": "Matrimonial",
        "keywords": ["divorce", "mutual consent", "matrimonial", "settlement"]
    },
    {
        "title": "Child Custody Battle",
        "description": "Divorced parents disputing custody of 6-year-old child. Both claiming to be better guardians.",
        "legal_issue": "Guardianship",
        "keywords": ["child custody", "guardianship", "divorce", "visitation"]
    },
    {
        "title": "Maintenance Claim",
        "description": "Wife seeking monthly maintenance of Rs 50,000 from husband. Husband claims inability to pay.",
        "legal_issue": "Maintenance",
        "keywords": ["maintenance", "alimony", "matrimonial", "support"]
    },
    {
        "title": "Adoption Case",
        "description": "Couple seeking to adopt 3-year-old orphan. All formalities completed, awaiting court approval.",
        "legal_issue": "Adoption",
        "keywords": ["adoption", "guardianship", "orphan", "child welfare"]
    },
    {
        "title": "Domestic Violence - Protection Order",
        "description": "Wife seeking protection order against abusive husband. Evidence of repeated violence and threats.",
        "legal_issue": "Domestic Violence Act",
        "keywords": ["domestic violence", "protection order", "abuse", "safety"]
    },
]

COMMERCIAL_CASES = [
    {
        "title": "Trademark Infringement",
        "description": "Company alleging competitor using confusingly similar trademark causing market confusion and revenue loss.",
        "legal_issue": "Intellectual Property",
        "keywords": ["trademark", "infringement", "IP", "brand"]
    },
    {
        "title": "Breach of Confidentiality",
        "description": "Former employee disclosed trade secrets to competitor. Non-compete agreement violated.",
        "legal_issue": "Contract Law",
        "keywords": ["confidentiality", "trade secrets", "non-compete", "breach"]
    },
    {
        "title": "Loan Recovery Suit",
        "description": "Bank seeking recovery of Rs 1 crore loan from defaulting company. Collateral seized.",
        "legal_issue": "Banking Law",
        "keywords": ["loan recovery", "default", "banking", "collateral"]
    },
    {
        "title": "Company Merger Dispute",
        "description": "Shareholders opposing merger deal alleging undervaluation and procedural irregularities.",
        "legal_issue": "Corporate Law",
        "keywords": ["merger", "corporate", "shareholders", "valuation"]
    },
    {
        "title": "Tax Evasion Case",
        "description": "Income Tax Department filed case for undeclared income of Rs 5 crores. Multiple offshore accounts discovered.",
        "legal_issue": "Tax Law",
        "keywords": ["tax evasion", "income tax", "undeclared income", "offshore"]
    },
]

def generate_case_number(case_type, index):
    """Generate realistic case number"""
    year = 2024
    type_codes = {
        "CRIMINAL": "CRM",
        "CIVIL": "CIV",
        "FAMILY": "FAM",
        "COMMERCIAL": "COM",
        "CONSTITUTIONAL": "CON"
    }
    code = type_codes.get(case_type, "MIS")
    return f"{code}/{year}/{str(index).zfill(4)}"

def get_priority_based_on_case(case_data):
    """Determine priority based on case keywords"""
    urgent_keywords = ["murder", "kidnapping", "rape", "robbery", "armed", "gun", "weapon"]
    high_keywords = ["fraud", "assault", "theft", "accident", "injury", "violence"]
    
    desc = case_data.get("description", "").lower()
    
    if any(kw in desc for kw in urgent_keywords):
        return "URGENT"
    elif any(kw in desc for kw in high_keywords):
        return "HIGH"
    elif random.random() < 0.3:
        return "HIGH"
    elif random.random() < 0.5:
        return "MEDIUM"
    else:
        return "LOW"

def get_track_based_on_description(description):
    """Determine DCM track based on case complexity"""
    fast_keywords = ["mutual consent", "simple", "routine", "minor", "traffic"]
    complex_keywords = ["murder", "fraud", "corruption", "multiple parties", "appeal"]
    
    desc = description.lower()
    
    if any(kw in desc for kw in fast_keywords):
        return "FAST"
    elif any(kw in desc for kw in complex_keywords):
        return "COMPLEX"
    else:
        return "REGULAR"

def estimate_duration(track):
    """Estimate hearing duration based on track"""
    durations = {
        "FAST": random.randint(30, 60),
        "REGULAR": random.randint(60, 120),
        "COMPLEX": random.randint(120, 240)
    }
    return durations.get(track, 90)

def create_dataset():
    """Generate 100+ cases and insert into MongoDB"""
    
    print("=" * 70)
    print("🚀 DCM SYSTEM - LARGE DATASET GENERATOR")
    print("=" * 70)
    print("\n📊 Generating 100+ realistic legal cases...")
    print("🏛️ Case Types: Criminal, Civil, Family, Commercial")
    print("\n")
    
    try:
        # Connect to MongoDB
        print("🔌 Connecting to MongoDB Atlas...")
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        print("✅ Connected successfully!\n")
        
        # Clear existing cases (optional)
        print("🗑️  Clearing existing cases...")
        db.cases.delete_many({})
        print(f"✅ Cleared {db.cases.estimated_document_count()} existing cases\n")
        
        cases_to_insert = []
        case_index = 1
        
        # Generate Criminal Cases (40 cases)
        print("⚖️  Generating Criminal Cases...")
        for i in range(40):
            template = random.choice(CRIMINAL_CASES)
            filing_date = date.today() - timedelta(days=random.randint(1, 365))
            priority = get_priority_based_on_case(template)
            track = get_track_based_on_description(template["description"])
            
            case = {
                "case_number": generate_case_number("CRIMINAL", case_index),
                "title": template["title"],
                "description": template["description"] + f" [Case filed on {filing_date}]",
                "synopsis": template["description"],
                "case_type": "CRIMINAL",
                "priority": priority,
                "status": random.choice(["FILED", "UNDER_REVIEW", "SCHEDULED"]),
                "filing_date": filing_date.isoformat(),
                "track": track,
                "estimated_duration_minutes": estimate_duration(track),
                "bns_section": template.get("bns_section", "Section 103"),
                "keywords": template.get("keywords", []),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            cases_to_insert.append(case)
            case_index += 1
        print(f"   ✅ Generated 40 criminal cases")
        
        # Generate Civil Cases (35 cases)
        print("📜 Generating Civil Cases...")
        for i in range(35):
            template = random.choice(CIVIL_CASES)
            filing_date = date.today() - timedelta(days=random.randint(1, 500))
            priority = random.choice(["MEDIUM", "HIGH", "LOW", "MEDIUM"])
            track = get_track_based_on_description(template["description"])
            
            case = {
                "case_number": generate_case_number("CIVIL", case_index),
                "title": template["title"],
                "description": template["description"] + f" [Filed {filing_date}]",
                "synopsis": template["description"],
                "case_type": "CIVIL",
                "priority": priority,
                "status": random.choice(["FILED", "UNDER_REVIEW", "SCHEDULED", "HEARING"]),
                "filing_date": filing_date.isoformat(),
                "track": track,
                "estimated_duration_minutes": estimate_duration(track),
                "legal_issue": template.get("legal_issue", "Civil Matter"),
                "keywords": template.get("keywords", []),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            cases_to_insert.append(case)
            case_index += 1
        print(f"   ✅ Generated 35 civil cases")
        
        # Generate Family Cases (15 cases)
        print("👨‍👩‍👧 Generating Family Cases...")
        for i in range(15):
            template = random.choice(FAMILY_CASES)
            filing_date = date.today() - timedelta(days=random.randint(1, 300))
            priority = random.choice(["HIGH", "MEDIUM", "MEDIUM"])
            track = get_track_based_on_description(template["description"])
            
            case = {
                "case_number": generate_case_number("FAMILY", case_index),
                "title": template["title"],
                "description": template["description"],
                "synopsis": template["description"],
                "case_type": "FAMILY",
                "priority": priority,
                "status": random.choice(["FILED", "UNDER_REVIEW", "SCHEDULED"]),
                "filing_date": filing_date.isoformat(),
                "track": track,
                "estimated_duration_minutes": estimate_duration(track),
                "legal_issue": template.get("legal_issue", "Family Matter"),
                "keywords": template.get("keywords", []),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            cases_to_insert.append(case)
            case_index += 1
        print(f"   ✅ Generated 15 family cases")
        
        # Generate Commercial Cases (12 cases)
        print("💼 Generating Commercial Cases...")
        for i in range(12):
            template = random.choice(COMMERCIAL_CASES)
            filing_date = date.today() - timedelta(days=random.randint(1, 400))
            priority = random.choice(["HIGH", "MEDIUM"])
            track = "COMPLEX"  # Most commercial cases are complex
            
            case = {
                "case_number": generate_case_number("COMMERCIAL", case_index),
                "title": template["title"],
                "description": template["description"],
                "synopsis": template["description"],
                "case_type": "COMMERCIAL",
                "priority": priority,
                "status": random.choice(["FILED", "UNDER_REVIEW", "SCHEDULED"]),
                "filing_date": filing_date.isoformat(),
                "track": track,
                "estimated_duration_minutes": estimate_duration(track),
                "legal_issue": template.get("legal_issue", "Commercial Dispute"),
                "keywords": template.get("keywords", []),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            cases_to_insert.append(case)
            case_index += 1
        print(f"   ✅ Generated 12 commercial cases")
        
        # Insert all cases
        print(f"\n💾 Inserting {len(cases_to_insert)} cases into database...")
        result = db.cases.insert_many(cases_to_insert)
        print(f"✅ Successfully inserted {len(result.inserted_ids)} cases!")
        
        # Print statistics
        print("\n" + "=" * 70)
        print("📊 DATASET STATISTICS")
        print("=" * 70)
        
        total = len(cases_to_insert)
        criminal = len([c for c in cases_to_insert if c["case_type"] == "CRIMINAL"])
        civil = len([c for c in cases_to_insert if c["case_type"] == "CIVIL"])
        family = len([c for c in cases_to_insert if c["case_type"] == "FAMILY"])
        commercial = len([c for c in cases_to_insert if c["case_type"] == "COMMERCIAL"])
        
        urgent = len([c for c in cases_to_insert if c["priority"] == "URGENT"])
        high = len([c for c in cases_to_insert if c["priority"] == "HIGH"])
        medium = len([c for c in cases_to_insert if c["priority"] == "MEDIUM"])
        low = len([c for c in cases_to_insert if c["priority"] == "LOW"])
        
        fast = len([c for c in cases_to_insert if c["track"] == "FAST"])
        regular = len([c for c in cases_to_insert if c["track"] == "REGULAR"])
        complex_track = len([c for c in cases_to_insert if c["track"] == "COMPLEX"])
        
        print(f"\n📈 Total Cases: {total}")
        print(f"\n🔹 By Case Type:")
        print(f"   • Criminal:    {criminal} ({criminal/total*100:.1f}%)")
        print(f"   • Civil:       {civil} ({civil/total*100:.1f}%)")
        print(f"   • Family:      {family} ({family/total*100:.1f}%)")
        print(f"   • Commercial:  {commercial} ({commercial/total*100:.1f}%)")
        
        print(f"\n🔹 By Priority:")
        print(f"   • Urgent:  {urgent} ({urgent/total*100:.1f}%)")
        print(f"   • High:    {high} ({high/total*100:.1f}%)")
        print(f"   • Medium:  {medium} ({medium/total*100:.1f}%)")
        print(f"   • Low:     {low} ({low/total*100:.1f}%)")
        
        print(f"\n🔹 By DCM Track:")
        print(f"   • Fast:     {fast} ({fast/total*100:.1f}%)")
        print(f"   • Regular:  {regular} ({regular/total*100:.1f}%)")
        print(f"   • Complex:  {complex_track} ({complex_track/total*100:.1f}%)")
        
        print("\n" + "=" * 70)
        print("✅ DATASET GENERATION COMPLETE!")
        print("=" * 70)
        print("\n🚀 Your DCM system now has 100+ realistic legal cases!")
        print("📋 You can view them at: http://localhost:3000/cases")
        print("🔍 Backend API: http://localhost:8001/docs")
        print("\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if 'client' in locals():
            client.close()
            print("🔌 MongoDB connection closed")

if __name__ == "__main__":
    print("\n")
    create_dataset()
    print("\n✨ Done! Press Enter to exit...")
    input()

"""
Intelligent Case Ingestion Service
Automatically detects case type, priority, and DCM track from case documents
"""

from typing import Dict, List, Optional, Tuple
import re
from datetime import datetime, date
from pymongo import MongoClient
from app.core.config import settings
import json


class CaseIngestionService:
    """
    Service to automatically ingest case files and classify them
    """
    
    # Keywords for case type detection
    CASE_TYPE_KEYWORDS = {
        "CRIMINAL": [
            "theft", "murder", "assault", "robbery", "kidnapping", "rape",
            "section 302", "section 376", "section 304", "fir", "police",
            "criminal", "accused", "arrest", "bail", "custody", "ipc",
            "bns", "section 303", "section 309", "dacoity", "burglary",
            "drugs", "narcotics", "ndps", "weapon", "gun", "knife"
        ],
        "CIVIL": [
            "property", "contract", "agreement", "plaintiff", "defendant",
            "damages", "compensation", "breach", "injunction", "specific performance",
            "suit", "civil", "decree", "partition", "easement", "title",
            "ownership", "possession", "eviction", "rent", "lease", "tort",
            "negligence", "defamation", "nuisance"
        ],
        "FAMILY": [
            "divorce", "custody", "maintenance", "alimony", "marriage",
            "matrimonial", "husband", "wife", "child", "adoption", "guardianship",
            "dowry", "domestic violence", "cruelty", "section 498a", "family",
            "visitation", "separation", "annulment", "spouse"
        ],
        "COMMERCIAL": [
            "company", "corporate", "partnership", "business", "commercial",
            "trademark", "copyright", "patent", "intellectual property",
            "arbitration", "contract", "joint venture", "merger", "acquisition",
            "shares", "shareholders", "directors", "insolvency", "bankruptcy",
            "debt recovery", "loan", "bank", "financial", "tax", "gst"
        ],
        "CONSTITUTIONAL": [
            "fundamental rights", "article", "constitution", "writ", "pil",
            "public interest litigation", "habeas corpus", "mandamus", "certiorari",
            "prohibition", "quo warranto", "constitutional", "supreme court",
            "high court", "judicial review", "ultra vires"
        ]
    }
    
    # Keywords for priority detection
    PRIORITY_KEYWORDS = {
        "URGENT": [
            "murder", "rape", "kidnapping", "life threatening", "armed robbery",
            "terrorism", "urgent", "immediate", "emergency", "critical",
            "death", "serious injury", "weapon", "child abuse", "trafficking"
        ],
        "HIGH": [
            "assault", "fraud", "cheating", "forgery", "bribery", "corruption",
            "domestic violence", "sexual harassment", "high value", "significant",
            "major", "substantial", "grievous hurt", "custodial", "habeas corpus"
        ],
        "MEDIUM": [
            "theft", "property dispute", "contract breach", "defamation",
            "trespass", "eviction", "maintenance", "moderate", "regular"
        ],
        "LOW": [
            "minor", "petty", "small claim", "routine", "simple", "uncontested",
            "mutual consent", "minimal", "nominal"
        ]
    }
    
    # BNS Section patterns
    BNS_SECTIONS = {
        "Section 103": ["murder", "homicide", "culpable homicide"],
        "Section 115": ["hurt", "assault", "battery", "injury"],
        "Section 137": ["kidnapping", "abduction"],
        "Section 303": ["theft", "stealing"],
        "Section 309": ["robbery", "dacoity"],
        "Section 316": ["cheating", "fraud", "deception"],
        "Section 354": ["sexual harassment", "outraging modesty"],
        "Section 376": ["rape", "sexual assault"],
        "Section 498A": ["cruelty", "dowry", "matrimonial cruelty"],
    }
    
    def __init__(self):
        """Initialize the ingestion service"""
        mongo_uri = settings.MONGODB_URL if settings.MONGODB_URL else \
            "mongodb+srv://vignesharivumani37:Vignesharivumani1230@cluster0.w7x5vdv.mongodb.net/dcm_system?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true"
        self.client = MongoClient(mongo_uri)
        self.db = self.client[settings.MONGODB_DATABASE]
        self.cases_collection = self.db.cases
    
    def detect_case_type(self, text: str) -> str:
        """
        Detect case type based on keywords in text
        """
        text_lower = text.lower()
        scores = {}
        
        for case_type, keywords in self.CASE_TYPE_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[case_type] = score
        
        # Return type with highest score, default to CIVIL if no match
        if max(scores.values()) == 0:
            return "CIVIL"
        
        return max(scores, key=scores.get)
    
    def detect_priority(self, text: str) -> str:
        """
        Detect case priority based on keywords
        """
        text_lower = text.lower()
        
        # Check in order: URGENT -> HIGH -> MEDIUM -> LOW
        for priority, keywords in self.PRIORITY_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                return priority
        
        return "MEDIUM"  # Default priority
    
    def detect_bns_section(self, text: str) -> Optional[str]:
        """
        Detect relevant BNS section from text
        """
        text_lower = text.lower()
        
        # First check for explicit section mentions
        section_pattern = r'section\s+(\d+[a-z]*)'
        matches = re.findall(section_pattern, text_lower)
        if matches:
            return f"Section {matches[0].upper()}"
        
        # Then check keyword-based detection
        for section, keywords in self.BNS_SECTIONS.items():
            if any(keyword in text_lower for keyword in keywords):
                return section
        
        return None
    
    def detect_track(self, text: str, case_type: str) -> str:
        """
        Determine DCM track (FAST/REGULAR/COMPLEX) based on case complexity
        """
        text_lower = text.lower()
        
        # Fast track indicators
        fast_keywords = [
            "mutual consent", "uncontested", "simple", "routine", "minor",
            "summary", "petty", "traffic", "bail", "interim"
        ]
        
        # Complex track indicators
        complex_keywords = [
            "murder", "multiple accused", "conspiracy", "organized crime",
            "appeal", "revision", "complex", "international", "corporate fraud",
            "constitutional", "pil", "corruption", "multiple parties"
        ]
        
        if any(kw in text_lower for kw in fast_keywords):
            return "FAST"
        elif any(kw in text_lower for kw in complex_keywords):
            return "COMPLEX"
        else:
            return "REGULAR"
    
    def estimate_duration(self, track: str) -> int:
        """
        Estimate hearing duration based on track
        """
        durations = {
            "FAST": 45,
            "REGULAR": 90,
            "COMPLEX": 180
        }
        return durations.get(track, 90)
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract relevant keywords from case text
        """
        text_lower = text.lower()
        keywords = set()
        
        # Extract all keywords that match from our dictionaries
        for case_type_keywords in self.CASE_TYPE_KEYWORDS.values():
            keywords.update([kw for kw in case_type_keywords if kw in text_lower])
        
        for priority_keywords in self.PRIORITY_KEYWORDS.values():
            keywords.update([kw for kw in priority_keywords if kw in text_lower])
        
        return list(keywords)[:10]  # Limit to top 10 keywords
    
    def generate_case_number(self, case_type: str) -> str:
        """
        Generate unique case number
        """
        year = date.today().year
        type_codes = {
            "CRIMINAL": "CRM",
            "CIVIL": "CIV",
            "FAMILY": "FAM",
            "COMMERCIAL": "COM",
            "CONSTITUTIONAL": "CON"
        }
        
        code = type_codes.get(case_type, "MIS")
        
        # Get count of cases of this type in current year
        count = self.cases_collection.count_documents({
            "case_type": case_type,
            "filing_date": {"$regex": f"^{year}"}
        })
        
        return f"{code}/{year}/{str(count + 1).zfill(4)}"
    
    def ingest_case(self, title: str, description: str, 
                   filing_date: Optional[date] = None,
                   additional_info: Optional[Dict] = None) -> Dict:
        """
        Main method to ingest a new case with automatic classification
        
        Args:
            title: Case title/headline
            description: Full case description/synopsis
            filing_date: Date case was filed (defaults to today)
            additional_info: Any additional metadata
        
        Returns:
            Dictionary with case details and classification results
        """
        
        # Combine title and description for analysis
        full_text = f"{title} {description}"
        
        # Automatic classification
        case_type = self.detect_case_type(full_text)
        priority = self.detect_priority(full_text)
        track = self.detect_track(full_text, case_type)
        bns_section = self.detect_bns_section(full_text)
        keywords = self.extract_keywords(full_text)
        duration = self.estimate_duration(track)
        case_number = self.generate_case_number(case_type)
        
        # Build case document
        case_doc = {
            "case_number": case_number,
            "title": title,
            "description": description,
            "synopsis": description[:500],  # First 500 chars
            "case_type": case_type,
            "priority": priority,
            "status": "FILED",
            "filing_date": (filing_date or date.today()).isoformat(),
            "track": track,
            "estimated_duration_minutes": duration,
            "keywords": keywords,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "auto_classified": True  # Flag to indicate auto-classification
        }
        
        # Add BNS section if detected
        if bns_section:
            case_doc["bns_section"] = bns_section
        
        # Merge additional info if provided
        if additional_info:
            case_doc.update(additional_info)
        
        # Insert into database
        result = self.cases_collection.insert_one(case_doc)
        case_doc["_id"] = str(result.inserted_id)
        
        return {
            "success": True,
            "case_id": str(result.inserted_id),
            "case_number": case_number,
            "classification": {
                "case_type": case_type,
                "priority": priority,
                "track": track,
                "bns_section": bns_section,
                "estimated_duration": duration
            },
            "case_details": case_doc
        }
    
    def ingest_bulk_cases(self, cases: List[Dict]) -> Dict:
        """
        Ingest multiple cases at once
        
        Args:
            cases: List of dicts with 'title' and 'description' keys
        
        Returns:
            Summary of ingestion results
        """
        results = {
            "total": len(cases),
            "success": 0,
            "failed": 0,
            "cases": []
        }
        
        for case_data in cases:
            try:
                result = self.ingest_case(
                    title=case_data.get("title", ""),
                    description=case_data.get("description", ""),
                    filing_date=case_data.get("filing_date"),
                    additional_info=case_data.get("additional_info")
                )
                results["success"] += 1
                results["cases"].append(result)
            except Exception as e:
                results["failed"] += 1
                results["cases"].append({
                    "success": False,
                    "error": str(e),
                    "title": case_data.get("title", "Unknown")
                })
        
        return results
    
    def ingest_from_json_file(self, filepath: str) -> Dict:
        """
        Ingest cases from a JSON file
        
        JSON format should be:
        [
            {"title": "...", "description": "...", "filing_date": "2024-01-01"},
            ...
        ]
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                cases = json.load(f)
            
            if not isinstance(cases, list):
                cases = [cases]
            
            return self.ingest_bulk_cases(cases)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def __del__(self):
        """Close MongoDB connection"""
        if hasattr(self, 'client'):
            self.client.close()


# Convenience functions for easy import
def ingest_case(title: str, description: str, **kwargs):
    """Quick function to ingest a single case"""
    service = CaseIngestionService()
    return service.ingest_case(title, description, **kwargs)


def ingest_bulk_cases(cases: List[Dict]):
    """Quick function to ingest multiple cases"""
    service = CaseIngestionService()
    return service.ingest_bulk_cases(cases)


def ingest_from_json(filepath: str):
    """Quick function to ingest from JSON file"""
    service = CaseIngestionService()
    return service.ingest_from_json_file(filepath)

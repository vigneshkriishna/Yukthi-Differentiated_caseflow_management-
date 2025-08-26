"""
NLP Service for BNS (Bharatiya Nyaya Sanhita) Section Suggestion
Phase 1: Rule/keyword-based IPC→BNS mapping stub
Phase 2+: TF-IDF + Linear SVM baseline
"""
from typing import List, Dict, Any, Optional
import re
import json
from pathlib import Path


class BNSSuggestion:
    """BNS section suggestion result"""
    def __init__(
        self,
        section_number: str,
        section_title: str,
        description: str,
        confidence: float,
        keywords_matched: List[str]
    ):
        self.section_number = section_number
        self.section_title = section_title
        self.description = description
        self.confidence = confidence
        self.keywords_matched = keywords_matched
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "section_number": self.section_number,
            "section_title": self.section_title,
            "description": self.description,
            "confidence": self.confidence,
            "keywords_matched": self.keywords_matched
        }


class BNSAssistService:
    """BNS Assist Service for legal section suggestions"""
    
    def __init__(self):
        self.bns_mapping = self._load_bns_mapping()
        self.keyword_patterns = self._compile_keyword_patterns()
    
    def _load_bns_mapping(self) -> Dict[str, Any]:
        """Load BNS section mapping data"""
        # In Phase 1, we'll use a hardcoded mapping
        # In production, this would load from a JSON file or database
        return {
            "sections": {
                "103": {
                    "title": "Murder",
                    "description": "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.",
                    "keywords": ["murder", "kill", "killing", "homicide", "death", "fatal", "deadly"],
                    "ipc_equivalent": "302"
                },
                "104": {
                    "title": "Punishment for murder by life-convict",
                    "description": "Whoever, being under sentence of imprisonment for life, commits murder, shall be punished with death.",
                    "keywords": ["murder", "life convict", "life sentence", "prisoner"],
                    "ipc_equivalent": "303"
                },
                "105": {
                    "title": "Culpable homicide not amounting to murder",
                    "description": "Whoever commits culpable homicide not amounting to murder shall be punished with imprisonment for life, or imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine.",
                    "keywords": ["culpable homicide", "manslaughter", "unintentional killing", "negligent death"],
                    "ipc_equivalent": "304"
                },
                "64": {
                    "title": "Theft",
                    "description": "Whoever intends to take dishonestly any moveable property out of the possession of any person without that person's consent, moves that property in order to such taking, is said to commit theft.",
                    "keywords": ["theft", "steal", "stealing", "stolen", "thief", "burglar", "burglary", "rob"],
                    "ipc_equivalent": "378"
                },
                "65": {
                    "title": "Punishment for theft",
                    "description": "Whoever commits theft shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.",
                    "keywords": ["theft", "steal", "stealing", "stolen"],
                    "ipc_equivalent": "379"
                },
                "69": {
                    "title": "Robbery",
                    "description": "In all robbery there is either theft or extortion. When theft is robbery, and when extortion is robbery.",
                    "keywords": ["robbery", "rob", "robber", "armed robbery", "dacoity", "gang robbery"],
                    "ipc_equivalent": "390"
                },
                "316": {
                    "title": "Voluntarily causing hurt",
                    "description": "Whoever voluntarily causes hurt shall be punished with imprisonment of either description for a term which may extend to one year, or with fine which may extend to one thousand rupees, or with both.",
                    "keywords": ["hurt", "assault", "battery", "violence", "injury", "harm", "attack"],
                    "ipc_equivalent": "323"
                },
                "322": {
                    "title": "Voluntarily causing grievous hurt",
                    "description": "Whoever voluntarily causes grievous hurt shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.",
                    "keywords": ["grievous hurt", "serious injury", "permanent disability", "severe assault"],
                    "ipc_equivalent": "322"
                },
                "63": {
                    "title": "Rape",
                    "description": "Whoever commits rape shall be punished with rigorous imprisonment of either description for a term which shall not be less than ten years, but which may extend to imprisonment for life, and shall also be liable to fine.",
                    "keywords": ["rape", "sexual assault", "molestation", "sexual harassment", "sexual violence"],
                    "ipc_equivalent": "376"
                },
                "318": {
                    "title": "Cheating",
                    "description": "Whoever cheats shall be punished with imprisonment of either description for a term which may extend to one year, or with fine, or with both.",
                    "keywords": ["cheat", "fraud", "deception", "forgery", "fake", "counterfeit", "scam"],
                    "ipc_equivalent": "420"
                },
                "61": {
                    "title": "Criminal breach of trust",
                    "description": "Whoever commits criminal breach of trust shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.",
                    "keywords": ["breach of trust", "embezzlement", "misappropriation", "fiduciary"],
                    "ipc_equivalent": "406"
                },
                "351": {
                    "title": "Kidnapping",
                    "description": "Kidnapping is of two kinds: kidnapping from lawful guardianship, and kidnapping from the country.",
                    "keywords": ["kidnapping", "abduction", "kidnap", "missing person", "forcible confinement"],
                    "ipc_equivalent": "359"
                },
                "137": {
                    "title": "Defamation",
                    "description": "Whoever defames another shall be punished with simple imprisonment for a term which may extend to two years, or with fine, or with both.",
                    "keywords": ["defamation", "libel", "slander", "character assassination", "reputation damage"],
                    "ipc_equivalent": "499"
                }
            }
        }
    
    def _compile_keyword_patterns(self) -> Dict[str, List[str]]:
        """Compile keyword patterns for efficient matching"""
        patterns = {}
        for section_num, section_data in self.bns_mapping["sections"].items():
            # Create regex patterns for each keyword
            keywords = section_data["keywords"]
            patterns[section_num] = [
                re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
                for keyword in keywords
            ]
        return patterns
    
    def suggest_bns_sections(
        self,
        case_synopsis: str,
        max_suggestions: int = 5
    ) -> List[BNSSuggestion]:
        """
        Suggest BNS sections based on case synopsis
        
        Args:
            case_synopsis: Text description of the case
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of BNSSuggestion objects
        """
        suggestions = []
        synopsis_lower = case_synopsis.lower()
        
        # Score each section based on keyword matches
        for section_num, patterns in self.keyword_patterns.items():
            section_data = self.bns_mapping["sections"][section_num]
            
            matched_keywords = []
            total_matches = 0
            
            # Count matches for each keyword
            for i, pattern in enumerate(patterns):
                matches = pattern.findall(case_synopsis)
                if matches:
                    keyword = section_data["keywords"][i]
                    matched_keywords.append(keyword)
                    total_matches += len(matches)
            
            # Calculate confidence score
            if matched_keywords:
                # Base confidence on number of unique keywords matched
                unique_keyword_score = len(matched_keywords) / len(section_data["keywords"])
                
                # Boost score based on total matches (repeated keywords)
                frequency_boost = min(total_matches / 10, 0.5)  # Cap at 0.5
                
                # Length penalty for very short synopsis
                length_penalty = 0 if len(case_synopsis) < 50 else 0.1
                
                confidence = min(0.95, unique_keyword_score + frequency_boost + length_penalty)
                
                suggestion = BNSSuggestion(
                    section_number=section_num,
                    section_title=section_data["title"],
                    description=section_data["description"],
                    confidence=round(confidence, 2),
                    keywords_matched=matched_keywords
                )
                
                suggestions.append(suggestion)
        
        # Sort by confidence score (highest first)
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        
        # Return top suggestions
        return suggestions[:max_suggestions]
    
    def get_section_details(self, section_number: str) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific BNS section
        
        Args:
            section_number: BNS section number
            
        Returns:
            Section details or None if not found
        """
        section_data = self.bns_mapping["sections"].get(section_number)
        if section_data:
            return {
                "section_number": section_number,
                "title": section_data["title"],
                "description": section_data["description"],
                "keywords": section_data["keywords"],
                "ipc_equivalent": section_data.get("ipc_equivalent")
            }
        return None
    
    def search_sections_by_keyword(
        self,
        keyword: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search BNS sections by keyword
        
        Args:
            keyword: Keyword to search for
            max_results: Maximum number of results
            
        Returns:
            List of matching sections
        """
        results = []
        keyword_lower = keyword.lower()
        
        for section_num, section_data in self.bns_mapping["sections"].items():
            # Check if keyword appears in title, description, or keywords
            title_match = keyword_lower in section_data["title"].lower()
            desc_match = keyword_lower in section_data["description"].lower()
            keyword_match = any(keyword_lower in kw.lower() for kw in section_data["keywords"])
            
            if title_match or desc_match or keyword_match:
                results.append({
                    "section_number": section_num,
                    "title": section_data["title"],
                    "description": section_data["description"][:200] + "..." if len(section_data["description"]) > 200 else section_data["description"],
                    "relevance_score": (
                        2.0 if title_match else 0 +
                        1.0 if keyword_match else 0 +
                        0.5 if desc_match else 0
                    )
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return results[:max_results]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the BNS mapping database"""
        sections = self.bns_mapping["sections"]
        
        total_sections = len(sections)
        total_keywords = sum(len(data["keywords"]) for data in sections.values())
        avg_keywords_per_section = total_keywords / total_sections if total_sections > 0 else 0
        
        # Group by crime category (simplified)
        crime_categories = {
            "violent": ["murder", "hurt", "rape", "assault", "robbery"],
            "property": ["theft", "burglary", "cheating", "fraud"],
            "personal": ["defamation", "kidnapping"],
            "financial": ["breach of trust", "embezzlement"]
        }
        
        category_counts = {}
        for category, category_keywords in crime_categories.items():
            count = 0
            for section_data in sections.values():
                if any(ck in " ".join(section_data["keywords"]).lower() 
                      for ck in category_keywords):
                    count += 1
            category_counts[category] = count
        
        return {
            "total_sections": total_sections,
            "total_keywords": total_keywords,
            "average_keywords_per_section": round(avg_keywords_per_section, 1),
            "category_distribution": category_counts,
            "version": "1.0.0",
            "last_updated": "2024-01-01"  # Placeholder
        }


# Global instance
bns_assist = BNSAssistService()

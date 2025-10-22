"""
Differentiated Case Management (DCM) Rules Engine
Classifies cases into Fast/Regular/Complex tracks based on predefined rules
"""
from typing import Any, Dict, List

from app.models.case import Case, CaseClassification, CasePriority, CaseTrack, CaseType


class DCMRulesEngine:
    """DCM Rules Engine for case classification"""

    def __init__(self):
        self.rules = self._initialize_rules()

    def _initialize_rules(self) -> Dict[str, Any]:
        """Initialize classification rules"""
        return {
            "fast_track_keywords": [
                "traffic violation", "minor dispute", "simple contract",
                "cheque bounce", "summary proceeding", "bail application",
                "interim order", "simple divorce", "rent dispute"
            ],
            "complex_track_keywords": [
                "murder", "rape", "fraud", "corruption", "conspiracy",
                "money laundering", "constitutional", "public interest",
                "class action", "corporate dispute", "intellectual property",
                "environmental", "cyber crime"
            ],
            "fast_track_case_types": [
                # Simple cases that can be resolved quickly
            ],
            "complex_track_case_types": [
                CaseType.CONSTITUTIONAL,
                CaseType.COMMERCIAL  # Large commercial disputes
            ],
            "priority_weights": {
                CasePriority.URGENT: 1.5,
                CasePriority.HIGH: 1.2,
                CasePriority.MEDIUM: 1.0,
                CasePriority.LOW: 0.8
            },
            "duration_thresholds": {
                "fast": 120,    # <= 2 hours
                "regular": 240, # <= 4 hours
                "complex": 480  # > 4 hours
            }
        }

    def classify_case(self, case: Case) -> CaseClassification:
        """
        Classify a case into Fast/Regular/Complex track

        Args:
            case: Case object to classify

        Returns:
            CaseClassification with track, score, and reasons
        """
        score = 0.0
        reasons = []

        # Keyword analysis in synopsis
        synopsis_lower = case.synopsis.lower()

        # Check for fast track keywords
        fast_keywords_found = []
        for keyword in self.rules["fast_track_keywords"]:
            if keyword in synopsis_lower:
                fast_keywords_found.append(keyword)
                score -= 2.0  # Negative score for fast track

        if fast_keywords_found:
            reasons.append(f"Fast track keywords found: {', '.join(fast_keywords_found)}")

        # Check for complex track keywords
        complex_keywords_found = []
        for keyword in self.rules["complex_track_keywords"]:
            if keyword in synopsis_lower:
                complex_keywords_found.append(keyword)
                score += 3.0  # Positive score for complex track

        if complex_keywords_found:
            reasons.append(f"Complex track keywords found: {', '.join(complex_keywords_found)}")

        # Case type analysis
        if case.case_type in self.rules["complex_track_case_types"]:
            score += 2.0
            reasons.append(f"Case type '{case.case_type}' typically requires complex handling")

        # Priority weight
        priority_weight = self.rules["priority_weights"].get(case.priority, 1.0)
        if priority_weight > 1.0:
            score += (priority_weight - 1.0) * 2
            reasons.append(f"High priority case (weight: {priority_weight})")
        elif priority_weight < 1.0:
            score -= (1.0 - priority_weight) * 1
            reasons.append(f"Lower priority case (weight: {priority_weight})")

        # Duration analysis
        duration = case.estimated_duration_minutes
        if duration <= self.rules["duration_thresholds"]["fast"]:
            score -= 1.0
            reasons.append(f"Short estimated duration ({duration} minutes)")
        elif duration >= self.rules["duration_thresholds"]["complex"]:
            score += 2.0
            reasons.append(f"Long estimated duration ({duration} minutes)")
        else:
            reasons.append(f"Medium estimated duration ({duration} minutes)")

        # Title analysis (simple heuristics)
        title_lower = case.title.lower()
        if any(word in title_lower for word in ["simple", "minor", "small"]):
            score -= 1.0
            reasons.append("Title suggests simple case")
        elif any(word in title_lower for word in ["complex", "major", "serious", "criminal"]):
            score += 1.5
            reasons.append("Title suggests complex case")

        # Determine track based on score
        if score <= -2.0:
            track = CaseTrack.FAST
            confidence = min(0.9, abs(score) / 5.0)
        elif score >= 3.0:
            track = CaseTrack.COMPLEX
            confidence = min(0.9, score / 8.0)
        else:
            track = CaseTrack.REGULAR
            confidence = 0.7  # Medium confidence for regular track

        # Ensure minimum reasons
        if not reasons:
            reasons = ["Standard case classification applied"]

        return CaseClassification(
            case_id=case.id,
            track=track,
            score=round(score, 2),
            reasons=reasons,
            confidence=round(confidence, 2)
        )

    def batch_classify_cases(self, cases: List[Case]) -> List[CaseClassification]:
        """
        Classify multiple cases

        Args:
            cases: List of cases to classify

        Returns:
            List of CaseClassification objects
        """
        return [self.classify_case(case) for case in cases]

    def get_classification_summary(self, cases: List[Case]) -> Dict[str, Any]:
        """
        Get summary statistics of case classifications

        Args:
            cases: List of cases to analyze

        Returns:
            Summary statistics dictionary
        """
        classifications = self.batch_classify_cases(cases)

        track_counts = {track.value: 0 for track in CaseTrack}
        total_score = 0.0
        total_confidence = 0.0

        for classification in classifications:
            track_counts[classification.track.value] += 1
            total_score += classification.score
            total_confidence += classification.confidence

        total_cases = len(classifications)

        return {
            "total_cases": total_cases,
            "track_distribution": track_counts,
            "track_percentages": {
                track: round((count / total_cases) * 100, 1) if total_cases > 0 else 0
                for track, count in track_counts.items()
            },
            "average_score": round(total_score / total_cases, 2) if total_cases > 0 else 0,
            "average_confidence": round(total_confidence / total_cases, 2) if total_cases > 0 else 0
        }


# Global instance
dcm_engine = DCMRulesEngine()

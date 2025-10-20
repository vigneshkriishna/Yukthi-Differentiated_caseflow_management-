"""
Enhanced BNS Assist Service with ML Model
Combines rule-based and ML-based BNS section prediction
"""
import os
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

# Import the model trainer
try:
    from .bns_model_trainer import BNSModelTrainer
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ ML dependencies not available, falling back to rule-based matching")

from .bns_training_data import get_training_data, get_section_details


class EnhancedBNSService:
    """Enhanced BNS service with ML capabilities"""
    
    def __init__(self, model_dir="./models"):
        self.model_dir = model_dir
        self.ml_trainer = None
        self.use_ml = False
        
        # Load training data for fallback
        self.training_data = get_training_data()
        self.sections_db = {item["section"]: item for item in self.training_data}
        
        # Try to load ML model if available
        if ML_AVAILABLE:
            self._try_load_ml_model()
        
        print(f"🤖 BNS Service initialized (ML: {'✅' if self.use_ml else '❌'})")
    
    def _try_load_ml_model(self):
        """Try to load the trained ML model"""
        try:
            self.ml_trainer = BNSModelTrainer(self.model_dir)
            self.ml_trainer.load_model()
            self.use_ml = True
            print("✅ ML model loaded successfully")
        except (FileNotFoundError, Exception) as e:
            print(f"⚠️ Could not load ML model: {e}")
            print("🔄 Will use rule-based matching as fallback")
            self.use_ml = False
    
    def train_ml_model(self):
        """Train the ML model"""
        if not ML_AVAILABLE:
            print("❌ ML dependencies not available for training")
            return False
        
        try:
            print("🏋️ Training BNS ML model...")
            self.ml_trainer = BNSModelTrainer(self.model_dir)
            accuracy, cv_scores = self.ml_trainer.train_model()
            self.ml_trainer.save_model()
            self.use_ml = True
            
            print(f"✅ Model trained with accuracy: {accuracy:.4f}")
            return True
        except Exception as e:
            print(f"❌ Error training model: {e}")
            return False
    
    def suggest_bns_sections(
        self,
        case_synopsis: str,
        max_suggestions: int = 5,
        min_confidence: float = 0.1
    ) -> List[Dict[str, Any]]:
        """
        Suggest BNS sections using ML or rule-based approach
        """
        if self.use_ml and self.ml_trainer:
            return self._ml_predict_sections(case_synopsis, max_suggestions, min_confidence)
        else:
            return self._rule_based_predict_sections(case_synopsis, max_suggestions)
    
    def _ml_predict_sections(
        self,
        case_synopsis: str,
        max_suggestions: int,
        min_confidence: float
    ) -> List[Dict[str, Any]]:
        """Use ML model for prediction"""
        try:
            predictions = self.ml_trainer.predict_section(case_synopsis, top_k=max_suggestions)
            
            # Filter by minimum confidence
            filtered_predictions = [
                pred for pred in predictions 
                if pred["confidence"] >= min_confidence
            ]
            
            # Format for API response
            suggestions = []
            for pred in filtered_predictions:
                suggestion = {
                    "section_number": pred["section_number"],
                    "section_title": pred["title"],
                    "description": pred["description"][:200] + "..." if len(pred["description"]) > 200 else pred["description"],
                    "confidence": round(pred["confidence"], 3),
                    "method": "ml_model",
                    "keywords_matched": self._extract_keywords(case_synopsis, pred["section_number"])
                }
                suggestions.append(suggestion)
            
            return suggestions
            
        except Exception as e:
            print(f"❌ ML prediction error: {e}, falling back to rule-based")
            return self._rule_based_predict_sections(case_synopsis, max_suggestions)
    
    def _rule_based_predict_sections(
        self,
        case_synopsis: str,
        max_suggestions: int
    ) -> List[Dict[str, Any]]:
        """Fallback rule-based prediction"""
        synopsis_lower = case_synopsis.lower()
        suggestions = []
        
        # Score each section based on keyword matches
        for section_num, section_data in self.sections_db.items():
            matched_keywords = []
            total_score = 0
            
            # Check examples for keyword matching
            for example in section_data["examples"]:
                example_words = set(example.lower().split())
                synopsis_words = set(synopsis_lower.split())
                
                # Calculate word overlap
                overlap = len(example_words.intersection(synopsis_words))
                if overlap > 2:  # At least 3 word overlap
                    matched_keywords.extend(list(example_words.intersection(synopsis_words)))
                    total_score += overlap
            
            # Direct keyword matching from title and description
            title_words = section_data["title"].lower().split()
            desc_words = section_data["description"].lower().split()
            
            for word in title_words + desc_words:
                if len(word) > 3 and word in synopsis_lower:
                    matched_keywords.append(word)
                    total_score += 2
            
            if matched_keywords:
                # Calculate confidence score
                unique_matches = len(set(matched_keywords))
                confidence = min(0.95, (total_score / 20) + (unique_matches / 10))
                
                suggestion = {
                    "section_number": section_num,
                    "section_title": section_data["title"],
                    "description": section_data["description"][:200] + "..." if len(section_data["description"]) > 200 else section_data["description"],
                    "confidence": round(confidence, 3),
                    "method": "rule_based",
                    "keywords_matched": list(set(matched_keywords))[:5]  # Top 5 keywords
                }
                suggestions.append(suggestion)
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        return suggestions[:max_suggestions]
    
    def _extract_keywords(self, text: str, section_number: str) -> List[str]:
        """Extract relevant keywords for a section"""
        section_data = self.sections_db.get(section_number)
        if not section_data:
            return []
        
        text_lower = text.lower()
        keywords = []
        
        # Extract keywords from section title
        for word in section_data["title"].lower().split():
            if len(word) > 3 and word in text_lower:
                keywords.append(word)
        
        return keywords[:5]
    
    def get_section_details(self, section_number: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific section"""
        section_data = self.sections_db.get(section_number)
        if not section_data:
            return None
        
        return {
            "section_number": section_number,
            "title": section_data["title"],
            "description": section_data["description"],
            "examples": section_data["examples"][:3],  # First 3 examples
            "total_examples": len(section_data["examples"])
        }
    
    def search_sections(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Search BNS sections by query"""
        query_lower = query.lower()
        results = []
        
        for section_num, section_data in self.sections_db.items():
            relevance_score = 0
            
            # Check title match
            if query_lower in section_data["title"].lower():
                relevance_score += 3
            
            # Check description match
            if query_lower in section_data["description"].lower():
                relevance_score += 2
            
            # Check examples match
            for example in section_data["examples"]:
                if query_lower in example.lower():
                    relevance_score += 1
                    break
            
            if relevance_score > 0:
                result = {
                    "section_number": section_num,
                    "title": section_data["title"],
                    "description": section_data["description"][:150] + "..." if len(section_data["description"]) > 150 else section_data["description"],
                    "relevance_score": relevance_score
                }
                results.append(result)
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:max_results]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics"""
        stats = {
            "total_sections": len(self.sections_db),
            "ml_model_available": self.use_ml,
            "sections_covered": list(self.sections_db.keys()),
            "method": "ml_model" if self.use_ml else "rule_based",
            "version": "2.0.0"
        }
        
        if self.use_ml and self.ml_trainer:
            ml_info = self.ml_trainer.get_model_info()
            stats.update({
                "model_info": ml_info,
                "feature_count": ml_info.get("feature_count", "Unknown")
            })
        
        return stats


# Global instance
enhanced_bns_service = EnhancedBNSService()


def initialize_bns_service():
    """Initialize BNS service and train model if needed"""
    print("🚀 Initializing Enhanced BNS Service...")
    
    if not enhanced_bns_service.use_ml and ML_AVAILABLE:
        print("🏋️ Training ML model for the first time...")
        success = enhanced_bns_service.train_ml_model()
        if success:
            print("✅ BNS ML model trained and ready!")
        else:
            print("⚠️ Using rule-based fallback")
    
    return enhanced_bns_service


if __name__ == "__main__":
    # Test the service
    service = initialize_bns_service()
    
    # Test cases
    test_cases = [
        "The accused murdered the victim by stabbing with a knife",
        "Theft of mobile phone from crowded market",
        "Online fraud involving fake investment scheme",
        "Domestic violence and harassment for dowry"
    ]
    
    print("\n🧪 Testing BNS Service:")
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case}")
        suggestions = service.suggest_bns_sections(case, max_suggestions=2)
        
        for j, suggestion in enumerate(suggestions, 1):
            print(f"   {j}. Section {suggestion['section_number']}: {suggestion['section_title']}")
            print(f"      Confidence: {suggestion['confidence']:.3f} | Method: {suggestion['method']}")
    
    # Print statistics
    print(f"\n📊 Service Statistics:")
    stats = service.get_statistics()
    for key, value in stats.items():
        if key != "sections_covered":
            print(f"   • {key}: {value}")

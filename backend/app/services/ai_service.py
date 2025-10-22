"""
AI Service for DCM System
Provides AI-powered features like case classification, document analysis, and recommendations
"""

import pickle
import json
import logging
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import re
from datetime import datetime

# ML and NLP imports
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import WordNetLemmatizer
    SKLEARN_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some ML libraries not available: {e}")
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)

class AIService:
    """Main AI service class for DCM system"""
    
    def __init__(self):
        self.model = None
        self.model_info = None
        self.vectorizer = None
        self.lemmatizer = WordNetLemmatizer()
        self._download_nltk_data()
        self._load_models()
    
    def _download_nltk_data(self):
        """Download required NLTK data"""
        try:
            nltk_data_path = Path.home() / 'nltk_data'
            nltk.data.path.append(str(nltk_data_path))
            
            required_data = ['punkt', 'stopwords', 'wordnet', 'omw-1.4']
            for data_name in required_data:
                try:
                    nltk.data.find(f'tokenizers/{data_name}')
                except LookupError:
                    try:
                        nltk.download(data_name, quiet=True)
                    except Exception as e:
                        logger.warning(f"Could not download NLTK data {data_name}: {e}")
                        
        except Exception as e:
            logger.warning(f"NLTK setup warning: {e}")
    
    def _load_models(self):
        """Load the enhanced BNS model and related components"""
        try:
            model_path = Path("models/enhanced_bns_model.pkl")
            info_path = Path("models/enhanced_model_info.json")
            
            if model_path.exists() and info_path.exists():
                # Load model
                with open(model_path, 'rb') as f:
                    model_data = pickle.load(f)
                
                # Load model info
                with open(info_path, 'r') as f:
                    self.model_info = json.load(f)
                
                # Extract components based on model structure
                if isinstance(model_data, dict):
                    self.model = model_data.get('classifier')
                    self.vectorizer = model_data.get('vectorizer')
                else:
                    self.model = model_data
                    # Create a basic TF-IDF vectorizer if not included
                    self.vectorizer = TfidfVectorizer(
                        max_features=5000,
                        ngram_range=(1, 3),
                        stop_words='english',
                        lowercase=True
                    )
                
                logger.info("✅ AI models loaded successfully")
                logger.info(f"📊 Model type: {self.model_info.get('model_type', 'Unknown')}")
                logger.info(f"🔢 Sections covered: {len(self.model_info.get('sections_covered', []))}")
                
            else:
                logger.warning("⚠️ AI models not found - creating basic classifiers")
                self._create_basic_models()
                
        except Exception as e:
            logger.error(f"❌ Error loading AI models: {e}")
            self._create_basic_models()
    
    def _create_basic_models(self):
        """Create basic models if main models are not available"""
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 3),
            stop_words='english',
            lowercase=True
        )
        
        # Basic model info
        self.model_info = {
            "model_type": "Basic DCM Classifier",
            "version": "1.0",
            "sections_covered": ["General", "Civil", "Criminal", "Family", "Commercial"],
            "features": "TF-IDF with basic classification"
        }
        
        logger.info("📝 Created basic AI models")
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for AI analysis"""
        if not text:
            return ""
        
        try:
            # Convert to lowercase
            text = text.lower()
            
            # Remove special characters but keep spaces
            text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
            
            # Remove extra whitespace
            text = ' '.join(text.split())
            
            # Tokenize and lemmatize
            try:
                tokens = word_tokenize(text)
                lemmatized = [self.lemmatizer.lemmatize(token) for token in tokens]
                return ' '.join(lemmatized)
            except Exception:
                # Fallback if NLTK operations fail
                return text
                
        except Exception as e:
            logger.warning(f"Text preprocessing error: {e}")
            return text
    
    async def classify_case(self, case_description: str, case_title: str = "") -> Dict:
        """
        Classify a case using the BNS model
        Returns classification results with confidence scores
        """
        try:
            # Combine title and description for better classification
            combined_text = f"{case_title} {case_description}".strip()
            processed_text = self.preprocess_text(combined_text)
            
            if not processed_text:
                return {
                    "predicted_section": "General",
                    "confidence": 0.5,
                    "top_predictions": [{"section": "General", "confidence": 0.5}],
                    "case_type": "General",
                    "suggested_priority": "medium"
                }
            
            # If we have the trained model, use it
            if self.model and self.vectorizer:
                try:
                    # Vectorize the text
                    if hasattr(self.vectorizer, 'transform'):
                        text_vector = self.vectorizer.transform([processed_text])
                    else:
                        # If vectorizer needs fitting, fit on the text
                        text_vector = self.vectorizer.fit_transform([processed_text])
                    
                    # Make prediction
                    if hasattr(self.model, 'predict_proba'):
                        probabilities = self.model.predict_proba(text_vector)[0]
                        prediction = self.model.predict(text_vector)[0]
                        confidence = max(probabilities)
                        
                        # Get top predictions
                        if hasattr(self.model, 'classes_'):
                            classes = self.model.classes_
                            top_indices = np.argsort(probabilities)[-5:][::-1]
                            top_predictions = [
                                {"section": classes[i], "confidence": float(probabilities[i])}
                                for i in top_indices
                            ]
                        else:
                            top_predictions = [{"section": str(prediction), "confidence": float(confidence)}]
                    else:
                        prediction = self.model.predict(text_vector)[0]
                        confidence = 0.8  # Default confidence for models without probability
                        top_predictions = [{"section": str(prediction), "confidence": confidence}]
                    
                    # Determine case type and priority based on classification
                    case_type, priority = self._determine_case_attributes(str(prediction), processed_text)
                    
                    return {
                        "predicted_section": str(prediction),
                        "confidence": float(confidence),
                        "top_predictions": top_predictions,
                        "case_type": case_type,
                        "suggested_priority": priority
                    }
                    
                except Exception as model_error:
                    logger.warning(f"Model prediction error: {model_error}")
                    # Fall back to rule-based classification
                    return self._rule_based_classification(processed_text, combined_text)
            
            else:
                # Use rule-based classification
                return self._rule_based_classification(processed_text, combined_text)
                
        except Exception as e:
            logger.error(f"Case classification error: {e}")
            return {
                "predicted_section": "General",
                "confidence": 0.5,
                "top_predictions": [{"section": "General", "confidence": 0.5}],
                "case_type": "General",
                "suggested_priority": "medium"
            }
    
    def _rule_based_classification(self, processed_text: str, original_text: str) -> Dict:
        """Rule-based classification as fallback"""
        
        # Define rule-based patterns
        patterns = {
            "Criminal": {
                "patterns": ["theft", "murder", "assault", "robbery", "fraud", "criminal", "accused", "defendant"],
                "sections": ["Section 103", "Section 304", "Section 318"],
                "priority": "high"
            },
            "Civil": {
                "patterns": ["property", "contract", "breach", "damages", "plaintiff", "civil", "dispute", "tort"],
                "sections": ["Section 101", "Section 137", "Section 140"],
                "priority": "medium"
            },
            "Family": {
                "patterns": ["divorce", "custody", "marriage", "family", "child", "spouse", "alimony"],
                "sections": ["Section 294", "Section 295"],
                "priority": "medium"
            },
            "Commercial": {
                "patterns": ["business", "company", "corporate", "commercial", "trade", "partnership"],
                "sections": ["Section 327", "Section 328"],
                "priority": "medium"
            }
        }
        
        # Score each category
        scores = {}
        for category, data in patterns.items():
            score = sum(1 for pattern in data["patterns"] if pattern in processed_text)
            if score > 0:
                scores[category] = score
        
        # Determine best match
        if scores:
            best_category = max(scores, key=scores.get)
            confidence = min(0.9, scores[best_category] / 5.0)  # Normalize to confidence
            predicted_section = patterns[best_category]["sections"][0]
            priority = patterns[best_category]["priority"]
        else:
            best_category = "General"
            predicted_section = "Section 101"
            confidence = 0.5
            priority = "medium"
        
        return {
            "predicted_section": predicted_section,
            "confidence": confidence,
            "top_predictions": [{"section": predicted_section, "confidence": confidence}],
            "case_type": best_category,
            "suggested_priority": priority
        }
    
    def _determine_case_attributes(self, prediction: str, text: str) -> Tuple[str, str]:
        """Determine case type and priority based on prediction and text"""
        
        # Map sections to case types (based on your BNS model)
        section_to_type = {
            "Section 103": "Criminal", "Section 304": "Criminal", "Section 318": "Criminal", "Section 319": "Criminal",
            "Section 101": "Civil", "Section 137": "Civil", "Section 140": "Civil",
            "Section 294": "Family", "Section 295": "Family",
            "Section 327": "Commercial", "Section 328": "Commercial"
        }
        
        case_type = section_to_type.get(prediction, "General")
        
        # Determine priority based on keywords
        high_priority_keywords = ["urgent", "emergency", "immediate", "murder", "assault", "fraud"]
        low_priority_keywords = ["routine", "standard", "minor", "simple"]
        
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in high_priority_keywords):
            priority = "high"
        elif any(keyword in text_lower for keyword in low_priority_keywords):
            priority = "low"
        elif case_type == "Criminal":
            priority = "high"
        else:
            priority = "medium"
        
        return case_type, priority
    
    async def analyze_document_content(self, content: str, filename: str) -> Dict:
        """
        Analyze document content and extract key information
        """
        try:
            processed_content = self.preprocess_text(content)
            
            # Extract key entities and information
            analysis = {
                "document_type": self._detect_document_type(content, filename),
                "key_entities": self._extract_entities(content),
                "summary": self._generate_summary(content),
                "sentiment": self._analyze_sentiment(processed_content),
                "word_count": len(content.split()),
                "readability_score": self._calculate_readability(content),
                "extracted_dates": self._extract_dates(content),
                "legal_keywords": self._extract_legal_keywords(content)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Document analysis error: {e}")
            return {
                "document_type": "Unknown",
                "key_entities": [],
                "summary": "Analysis not available",
                "sentiment": "neutral",
                "word_count": 0,
                "readability_score": 0,
                "extracted_dates": [],
                "legal_keywords": []
            }
    
    def _detect_document_type(self, content: str, filename: str) -> str:
        """Detect the type of legal document"""
        
        content_lower = content.lower()
        
        type_patterns = {
            "Petition": ["petition", "petitioner", "pray", "relief sought"],
            "Judgment": ["judgment", "judgement", "court orders", "hereby ordered"],
            "Pleading": ["pleading", "statement of claim", "defence", "counter claim"],
            "Contract": ["agreement", "contract", "terms and conditions", "whereas"],
            "Evidence": ["exhibit", "evidence", "witness statement", "affidavit"],
            "Notice": ["notice", "summons", "citation", "hereby notified"],
            "Brief": ["brief", "argument", "case law", "precedent"],
            "Order": ["order", "court order", "interim order", "final order"]
        }
        
        for doc_type, patterns in type_patterns.items():
            if any(pattern in content_lower for pattern in patterns):
                return doc_type
        
        # Check filename for hints
        filename_lower = filename.lower()
        for doc_type in type_patterns.keys():
            if doc_type.lower() in filename_lower:
                return doc_type
        
        return "General Legal Document"
    
    def _extract_entities(self, content: str) -> List[Dict]:
        """Extract entities like names, dates, amounts, etc."""
        entities = []
        
        # Extract potential names (capitalize words)
        name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        names = re.findall(name_pattern, content)
        
        # Filter common legal terms
        legal_stopwords = {'Court', 'Judge', 'Justice', 'Honorable', 'Section', 'Act', 'Rule', 'Order'}
        names = [name for name in names if name not in legal_stopwords and len(name) > 2]
        
        for name in set(names[:10]):  # Limit to top 10
            entities.append({"type": "Person", "value": name})
        
        # Extract amounts
        amount_pattern = r'(?:Rs\.?|₹|\$)\s*(\d+(?:,\d+)*(?:\.\d+)?)'
        amounts = re.findall(amount_pattern, content, re.IGNORECASE)
        for amount in amounts:
            entities.append({"type": "Amount", "value": f"₹{amount}"})
        
        # Extract case numbers
        case_pattern = r'(?:Case|FIR|Complaint)[\s\w]*?No\.?\s*(\w+/\d+/\d+|\d+/\d+)'
        case_numbers = re.findall(case_pattern, content, re.IGNORECASE)
        for case_num in case_numbers:
            entities.append({"type": "Case Number", "value": case_num})
        
        return entities
    
    def _generate_summary(self, content: str) -> str:
        """Generate a brief summary of the document"""
        try:
            sentences = sent_tokenize(content)
            if len(sentences) <= 3:
                return content
            
            # Simple extractive summarization
            # Take the first sentence, a middle sentence, and potentially the last
            summary_sentences = []
            
            if sentences:
                summary_sentences.append(sentences[0])  # First sentence
            
            if len(sentences) > 5:
                mid_idx = len(sentences) // 2
                summary_sentences.append(sentences[mid_idx])  # Middle sentence
            
            if len(sentences) > 2:
                summary_sentences.append(sentences[-1])  # Last sentence
            
            return " ".join(summary_sentences)
            
        except Exception:
            # Fallback: return first 200 characters
            return content[:200] + "..." if len(content) > 200 else content
    
    def _analyze_sentiment(self, content: str) -> str:
        """Basic sentiment analysis"""
        
        positive_words = ['agree', 'accept', 'approve', 'satisfied', 'success', 'win', 'favorable']
        negative_words = ['dispute', 'deny', 'reject', 'fail', 'violation', 'breach', 'guilty', 'liable']
        
        content_lower = content.lower()
        
        pos_count = sum(1 for word in positive_words if word in content_lower)
        neg_count = sum(1 for word in negative_words if word in content_lower)
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"
    
    def _calculate_readability(self, content: str) -> float:
        """Simple readability score based on sentence and word length"""
        try:
            sentences = sent_tokenize(content)
            words = content.split()
            
            if not sentences or not words:
                return 0
            
            avg_sentence_length = len(words) / len(sentences)
            avg_word_length = sum(len(word) for word in words) / len(words)
            
            # Simple readability formula (lower is easier to read)
            score = avg_sentence_length * 0.39 + avg_word_length * 11.8 - 15.59
            return max(0, min(100, score))
            
        except Exception:
            return 50  # Default neutral score
    
    def _extract_dates(self, content: str) -> List[str]:
        """Extract dates from content"""
        
        # Various date patterns
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # DD/MM/YYYY or MM/DD/YYYY
            r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}\b',  # DD Month YYYY
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{2,4}\b',  # Month DD, YYYY
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            dates.extend(matches)
        
        return list(set(dates))  # Remove duplicates
    
    def _extract_legal_keywords(self, content: str) -> List[str]:
        """Extract important legal keywords and phrases"""
        
        legal_terms = [
            'plaintiff', 'defendant', 'petitioner', 'respondent', 'appellant', 'court',
            'judgment', 'order', 'decree', 'injunction', 'damages', 'compensation',
            'evidence', 'witness', 'testimony', 'affidavit', 'contract', 'agreement',
            'breach', 'violation', 'liability', 'negligence', 'jurisdiction',
            'appeal', 'revision', 'writ', 'habeas corpus', 'mandamus', 'certiorari'
        ]
        
        content_lower = content.lower()
        found_terms = [term for term in legal_terms if term in content_lower]
        
        return found_terms
    
    async def find_similar_cases(self, case_description: str, case_title: str = "", limit: int = 5, all_cases: List[Any] = None) -> List[Dict]:
        """
        Find similar cases using text similarity
        """
        try:
            # Use provided cases or return empty list
            if not all_cases:
                return []
            
            # Prepare query text
            query_text = f"{case_title} {case_description}".strip()
            processed_query = self.preprocess_text(query_text)
            
            # Prepare case texts
            case_texts = []
            case_data = []
            
            for case in all_cases:
                case_text = f"{case.title} {case.description}".strip()
                processed_case_text = self.preprocess_text(case_text)
                
                if processed_case_text:  # Only include cases with meaningful text
                    case_texts.append(processed_case_text)
                    case_data.append({
                        "id": str(case.id),
                        "case_number": case.case_number,
                        "title": case.title,
                        "description": case.description,
                        "case_type": case.case_type,
                        "status": case.status,
                        "created_at": case.created_at
                    })
            
            if not case_texts or not SKLEARN_AVAILABLE:
                return []
            
            # Calculate similarity using TF-IDF
            all_texts = [processed_query] + case_texts
            
            # Use existing vectorizer or create new one
            if self.vectorizer and hasattr(self.vectorizer, 'fit_transform'):
                tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            else:
                from sklearn.feature_extraction.text import TfidfVectorizer
                vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
                tfidf_matrix = vectorizer.fit_transform(all_texts)
            
            # Calculate cosine similarity
            similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
            
            # Get top similar cases
            similar_indices = similarity_scores.argsort()[-limit:][::-1]
            
            similar_cases = []
            for idx in similar_indices:
                if similarity_scores[idx] > 0.1:  # Minimum similarity threshold
                    case_info = case_data[idx].copy()
                    case_info["similarity_score"] = float(similarity_scores[idx])
                    similar_cases.append(case_info)
            
            return similar_cases
            
        except Exception as e:
            logger.error(f"Similar cases search error: {e}")
            return []
    
    async def generate_case_insights(self, case_data: Dict, all_cases: List[Any] = None) -> Dict:
        """
        Generate AI insights for a specific case
        """
        try:
            if not case_data:
                return {"error": "Case data not provided"}
            
            case_description = case_data.get("description", "")
            case_title = case_data.get("title", "")
            case_id = case_data.get("id", "")
            
            # Classify the case
            classification = await self.classify_case(case_description, case_title)
            
            # Find similar cases
            similar_cases = await self.find_similar_cases(case_description, case_title, limit=3, all_cases=all_cases)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(case_data, classification, similar_cases)
            
            # Analyze case complexity
            complexity_analysis = self._analyze_case_complexity(case_description, case_title)
            
            return {
                "case_id": case_id,
                "classification": classification,
                "similar_cases": similar_cases,
                "recommendations": recommendations,
                "complexity_analysis": complexity_analysis,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Case insights generation error: {e}")
            return {"error": str(e)}
    
    def _generate_recommendations(self, case_data: Dict, classification: Dict, similar_cases: List[Dict]) -> List[str]:
        """Generate actionable recommendations for the case"""
        
        recommendations = []
        
        # Priority-based recommendations
        if classification.get("suggested_priority") == "high":
            recommendations.append("🚨 High priority case - consider expedited processing")
            recommendations.append("📅 Schedule hearing within 2 weeks")
        
        # Case type specific recommendations
        case_type = classification.get("case_type", "")
        if case_type == "Criminal":
            recommendations.append("👮 Ensure all criminal procedures are followed")
            recommendations.append("📋 Verify evidence chain of custody")
        elif case_type == "Civil":
            recommendations.append("💼 Review civil procedure requirements")
            recommendations.append("📄 Check for mandatory documentation")
        elif case_type == "Family":
            recommendations.append("👨‍👩‍👧‍👦 Consider mediation for family matters")
            recommendations.append("🤝 Explore settlement options")
        
        # Similar cases recommendations
        if similar_cases:
            recommendations.append(f"📚 Review {len(similar_cases)} similar cases for precedent")
            recent_similar = [c for c in similar_cases if c.get("similarity_score", 0) > 0.3]
            if recent_similar:
                recommendations.append("⚖️ High similarity cases found - review their outcomes")
        
        # Status-based recommendations
        case_status = case_data.get("status", "")
        if case_status == "pending":
            recommendations.append("⏰ Case pending - assign judge and schedule initial hearing")
        elif case_status == "in_progress":
            recommendations.append("📈 Case in progress - monitor deadlines and milestones")
        
        return recommendations[:6]  # Limit to 6 recommendations
    
    def _analyze_case_complexity(self, description: str, title: str) -> Dict:
        """Analyze the complexity of a case"""
        
        combined_text = f"{title} {description}".lower()
        
        # Complexity indicators
        complex_keywords = [
            'multiple parties', 'cross-claim', 'counter-claim', 'class action',
            'constitutional', 'international', 'corporate', 'merger', 'acquisition',
            'intellectual property', 'patent', 'copyright', 'trademark',
            'securities', 'fraud', 'conspiracy', 'racketeering'
        ]
        
        simple_keywords = [
            'traffic violation', 'minor', 'simple', 'straightforward',
            'routine', 'standard procedure', 'uncontested'
        ]
        
        # Calculate complexity score
        complex_score = sum(1 for keyword in complex_keywords if keyword in combined_text)
        simple_score = sum(1 for keyword in simple_keywords if keyword in combined_text)
        
        # Text length indicators
        word_count = len(description.split())
        
        # Overall complexity assessment
        if complex_score > simple_score and word_count > 500:
            complexity_level = "High"
            estimated_duration = "6-12 months"
        elif simple_score > complex_score or word_count < 100:
            complexity_level = "Low"
            estimated_duration = "1-3 months"
        else:
            complexity_level = "Medium"
            estimated_duration = "3-6 months"
        
        return {
            "complexity_level": complexity_level,
            "estimated_duration": estimated_duration,
            "word_count": word_count,
            "complexity_indicators": complex_score,
            "simplicity_indicators": simple_score
        }


# Global AI service instance
ai_service = AIService()

# Export the service
__all__ = ['AIService', 'ai_service']
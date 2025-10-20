"""
BNS Ensemble Model for Legal Case Classification
Enhanced ensemble approach with TF-IDF, Random Forest, and rule-based classification
Day 2 of Capstone Project - Production-ready ML model
"""

import json
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Core ML libraries
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

@dataclass
class PredictionResult:
    """Structured prediction result with confidence scoring"""
    bns_section: str
    confidence: float
    punishment: str
    severity: str
    reasoning: List[str]
    rule_based_match: bool
    ensemble_scores: Dict[str, float]

class BNSEnsembleClassifier:
    """
    Advanced ensemble classifier for BNS section prediction
    Combines TF-IDF + Logistic Regression, Random Forest, and rule-based classification
    """
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95
        )
        
        # Individual classifiers
        self.logistic_classifier = LogisticRegression(
            random_state=42,
            max_iter=1000,
            C=1.0
        )
        
        self.rf_classifier = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2
        )
        
        # Ensemble voting classifier
        self.ensemble_classifier = VotingClassifier(
            estimators=[
                ('logistic', self.logistic_classifier),
                ('random_forest', self.rf_classifier)
            ],
            voting='soft'  # Use probability predictions
        )
        
        self.label_encoder = LabelEncoder()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Model artifacts
        self.is_trained = False
        self.feature_names = []
        self.class_names = []
        self.bns_mapping = {}
        self.punishment_mapping = {}
        self.training_metadata = {}
        
        # Rule-based patterns for high-confidence matching
        self.rule_patterns = {
            '303(2)': ['theft', 'stolen', 'snatched', 'rob', 'steal'],
            '318(4)': ['fraud', 'cheating', 'fake', 'impersonation', 'deceive'],
            '326': ['assault', 'hurt', 'weapon', 'attack', 'violence'],
            '331': ['house-breaking', 'burglary', 'break', 'enter'],
            '336': ['forgery', 'fake document', 'forged', 'false certificate'],
            '309(4)': ['robbery', 'gunpoint', 'armed', 'threatening'],
            '354': ['molestation', 'inappropriate touch', 'sexual harassment'],
            '103(1)': ['murder', 'killed', 'homicide', 'death'],
            '370': ['trafficking', 'human trafficking', 'forced labor'],
            '364A': ['kidnapping', 'ransom', 'abduction']
        }
    
    def preprocess_text(self, text: str) -> str:
        """Advanced text preprocessing for legal documents"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Tokenization
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        processed_tokens = []
        for token in tokens:
            if token.isalpha() and token not in self.stop_words and len(token) > 2:
                lemmatized = self.lemmatizer.lemmatize(token)
                processed_tokens.append(lemmatized)
        
        return ' '.join(processed_tokens)
    
    def extract_features(self, case_data: Dict) -> str:
        """Extract and combine relevant features from case data"""
        features = []
        
        # Primary text features
        if 'description' in case_data:
            features.append(case_data['description'])
        
        if 'title' in case_data:
            features.append(case_data['title'])
        
        # Case type and severity
        if 'case_type' in case_data:
            features.append(f"case_type_{case_data['case_type']}")
        
        if 'severity' in case_data:
            features.append(f"severity_{case_data['severity']}")
        
        # Evidence types
        if 'evidence' in case_data and isinstance(case_data['evidence'], list):
            evidence_text = ' '.join(case_data['evidence'])
            features.append(f"evidence_{evidence_text}")
        
        combined_text = ' '.join(features)
        return self.preprocess_text(combined_text)
    
    def rule_based_prediction(self, text: str) -> Optional[Tuple[str, float, List[str]]]:
        """Rule-based classification for high-confidence cases"""
        text_lower = text.lower()
        reasoning = []
        
        for bns_section, patterns in self.rule_patterns.items():
            matches = 0
            matched_patterns = []
            
            for pattern in patterns:
                if pattern in text_lower:
                    matches += 1
                    matched_patterns.append(pattern)
            
            # High confidence if multiple patterns match
            if matches >= 2:
                confidence = min(0.95, 0.7 + (matches * 0.05))
                reasoning = [f"Rule-based match: {', '.join(matched_patterns)}"]
                return bns_section, confidence, reasoning
            
            # Medium confidence for single strong pattern
            elif matches == 1 and len(matched_patterns[0]) > 4:
                confidence = 0.75
                reasoning = [f"Strong rule-based match: {matched_patterns[0]}"]
                return bns_section, confidence, reasoning
        
        return None
    
    def load_training_data(self, dataset_path: str) -> Tuple[List[str], List[str]]:
        """Load and prepare training data from JSON dataset"""
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.bns_mapping = data.get('bns_mapping', {})
        
        features = []
        labels = []
        
        for case in data['cases']:
            # Extract features
            feature_text = self.extract_features(case)
            features.append(feature_text)
            
            # Extract label
            bns_section = case.get('bns_section', 'unknown')
            labels.append(bns_section)
            
            # Store punishment mapping
            if bns_section not in self.punishment_mapping:
                self.punishment_mapping[bns_section] = {
                    'punishment': case.get('punishment', 'Not specified'),
                    'severity': case.get('severity', 'medium')
                }
        
        return features, labels
    
    def train(self, dataset_path: str) -> Dict:
        """Train the ensemble model with comprehensive evaluation"""
        print("🔄 Loading training data...")
        features, labels = self.load_training_data(dataset_path)
        
        print(f"📊 Dataset size: {len(features)} cases")
        print(f"📊 Unique BNS sections: {len(set(labels))}")
        
        # Encode labels
        labels_encoded = self.label_encoder.fit_transform(labels)
        self.class_names = self.label_encoder.classes_
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels_encoded, test_size=0.2, random_state=42, stratify=labels_encoded
        )
        
        print("🔄 Training TF-IDF vectorizer...")
        X_train_tfidf = self.tfidf_vectorizer.fit_transform(X_train)
        X_test_tfidf = self.tfidf_vectorizer.transform(X_test)
        
        self.feature_names = self.tfidf_vectorizer.get_feature_names_out()
        
        print("🔄 Training ensemble classifier...")
        self.ensemble_classifier.fit(X_train_tfidf, y_train)
        
        # Evaluate model
        print("📈 Evaluating model performance...")
        y_pred = self.ensemble_classifier.predict(X_test_tfidf)
        y_pred_proba = self.ensemble_classifier.predict_proba(X_test_tfidf)
        
        accuracy = accuracy_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(self.ensemble_classifier, X_train_tfidf, y_train, cv=5)
        
        # Detailed classification report
        class_report = classification_report(
            y_test, y_pred, 
            target_names=self.class_names, 
            output_dict=True
        )
        
        self.training_metadata = {
            'training_date': datetime.now().isoformat(),
            'dataset_size': len(features),
            'test_accuracy': accuracy,
            'cv_mean_accuracy': cv_scores.mean(),
            'cv_std_accuracy': cv_scores.std(),
            'num_features': len(self.feature_names),
            'num_classes': len(self.class_names),
            'classification_report': class_report
        }
        
        self.is_trained = True
        
        print(f"✅ Training completed!")
        print(f"📊 Test Accuracy: {accuracy:.4f}")
        print(f"📊 CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
        
        return self.training_metadata
    
    def predict(self, case_data: Dict) -> PredictionResult:
        """Make prediction with confidence scoring and reasoning"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Extract features
        feature_text = self.extract_features(case_data)
        
        # Try rule-based prediction first
        rule_result = self.rule_based_prediction(feature_text)
        
        if rule_result:
            bns_section, confidence, reasoning = rule_result
            punishment_info = self.punishment_mapping.get(bns_section, {})
            
            return PredictionResult(
                bns_section=bns_section,
                confidence=confidence,
                punishment=punishment_info.get('punishment', 'Not specified'),
                severity=punishment_info.get('severity', 'medium'),
                reasoning=reasoning,
                rule_based_match=True,
                ensemble_scores={'rule_based': confidence}
            )
        
        # Use ensemble model
        feature_vector = self.tfidf_vectorizer.transform([feature_text])
        
        # Get predictions and probabilities
        prediction = self.ensemble_classifier.predict(feature_vector)[0]
        probabilities = self.ensemble_classifier.predict_proba(feature_vector)[0]
        
        # Get individual classifier scores
        logistic_proba = self.logistic_classifier.predict_proba(feature_vector)[0]
        rf_proba = self.rf_classifier.predict_proba(feature_vector)[0]
        
        predicted_bns = self.label_encoder.inverse_transform([prediction])[0]
        confidence = probabilities[prediction]
        
        # Get top features for reasoning
        feature_importance = self.get_feature_importance(feature_vector, predicted_bns)
        
        punishment_info = self.punishment_mapping.get(predicted_bns, {})
        
        return PredictionResult(
            bns_section=predicted_bns,
            confidence=confidence,
            punishment=punishment_info.get('punishment', 'Not specified'),
            severity=punishment_info.get('severity', 'medium'),
            reasoning=feature_importance[:3],  # Top 3 features
            rule_based_match=False,
            ensemble_scores={
                'ensemble': confidence,
                'logistic': logistic_proba[prediction],
                'random_forest': rf_proba[prediction]
            }
        )
    
    def get_feature_importance(self, feature_vector, predicted_class: str) -> List[str]:
        """Get important features that contributed to the prediction"""
        # Get feature weights from logistic regression
        class_idx = self.label_encoder.transform([predicted_class])[0]
        
        # Get coefficients for the predicted class
        coefficients = self.logistic_classifier.coef_[class_idx]
        
        # Get feature values
        feature_values = feature_vector.toarray()[0]
        
        # Calculate feature contributions
        contributions = coefficients * feature_values
        
        # Get top contributing features
        top_indices = np.argsort(contributions)[-5:][::-1]
        
        important_features = []
        for idx in top_indices:
            if contributions[idx] > 0:
                feature_name = self.feature_names[idx]
                importance = contributions[idx]
                important_features.append(f"{feature_name} (weight: {importance:.3f})")
        
        return important_features
    
    def save_model(self, model_path: str):
        """Save the trained model to disk"""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        model_data = {
            'tfidf_vectorizer': self.tfidf_vectorizer,
            'ensemble_classifier': self.ensemble_classifier,
            'label_encoder': self.label_encoder,
            'bns_mapping': self.bns_mapping,
            'punishment_mapping': self.punishment_mapping,
            'rule_patterns': self.rule_patterns,
            'training_metadata': self.training_metadata,
            'is_trained': self.is_trained
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✅ Model saved to {model_path}")
    
    def load_model(self, model_path: str):
        """Load a pre-trained model from disk"""
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.tfidf_vectorizer = model_data['tfidf_vectorizer']
        self.ensemble_classifier = model_data['ensemble_classifier']
        self.label_encoder = model_data['label_encoder']
        self.bns_mapping = model_data['bns_mapping']
        self.punishment_mapping = model_data['punishment_mapping']
        self.rule_patterns = model_data['rule_patterns']
        self.training_metadata = model_data['training_metadata']
        self.is_trained = model_data['is_trained']
        
        # Reconstruct derived attributes
        if self.is_trained:
            self.feature_names = self.tfidf_vectorizer.get_feature_names_out()
            self.class_names = self.label_encoder.classes_
        
        print(f"✅ Model loaded from {model_path}")
    
    def get_model_info(self) -> Dict:
        """Get comprehensive model information"""
        if not self.is_trained:
            return {"status": "untrained"}
        
        return {
            "status": "trained",
            "training_metadata": self.training_metadata,
            "model_components": {
                "tfidf_features": len(self.feature_names),
                "classes": len(self.class_names),
                "rule_patterns": len(self.rule_patterns)
            },
            "bns_sections_supported": list(self.bns_mapping.keys()),
            "accuracy_metrics": {
                "test_accuracy": self.training_metadata.get('test_accuracy', 0),
                "cv_accuracy": self.training_metadata.get('cv_mean_accuracy', 0)
            }
        }

# Example usage and testing
def test_ensemble_model():
    """Test the ensemble model with sample data"""
    
    # Initialize model
    model = BNSEnsembleClassifier()
    
    # Test case
    test_case = {
        "case_id": "TEST001",
        "title": "State vs. Test Accused",
        "description": "Theft of mobile phone from public transport by snatching",
        "severity": "medium",
        "case_type": "theft",
        "evidence": ["CCTV footage", "witness statements"]
    }
    
    print("🔬 Testing BNS Ensemble Model")
    print("=" * 50)
    
    # Load and train model
    dataset_path = "../../data/capstone_dataset/complete_enhanced_dataset.json"
    
    try:
        print("📚 Training model...")
        training_results = model.train(dataset_path)
        
        print("\n🔍 Making prediction...")
        result = model.predict(test_case)
        
        print(f"\n📋 PREDICTION RESULTS")
        print(f"BNS Section: {result.bns_section}")
        print(f"Confidence: {result.confidence:.4f}")
        print(f"Punishment: {result.punishment}")
        print(f"Severity: {result.severity}")
        print(f"Rule-based: {result.rule_based_match}")
        print(f"Reasoning: {result.reasoning}")
        print(f"Ensemble Scores: {result.ensemble_scores}")
        
        # Model info
        print(f"\n📊 MODEL INFORMATION")
        model_info = model.get_model_info()
        print(f"Test Accuracy: {model_info['accuracy_metrics']['test_accuracy']:.4f}")
        print(f"CV Accuracy: {model_info['accuracy_metrics']['cv_accuracy']:.4f}")
        print(f"Supported BNS Sections: {len(model_info['bns_sections_supported'])}")
        
        return model
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    test_ensemble_model()

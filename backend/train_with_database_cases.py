"""
Train BNS Model using REAL cases from MongoDB Database
This will use the 102 cases we generated for much better accuracy!
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pymongo import MongoClient
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
import pickle
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import config
import config
CONFIG = config.Config()
MONGODB_URL = CONFIG.MONGODB_URL
DATABASE_NAME = CONFIG.DATABASE_NAME

class EnhancedBNSClassifierV2:
    """Enhanced classifier trained on real database cases"""
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=2000,
            stop_words='english',
            ngram_range=(1, 3),
            min_df=1,
            max_df=0.95
        )
        self.rf_classifier = RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            max_depth=15,
            min_samples_split=2,
            min_samples_leaf=1,
            class_weight='balanced'
        )
        self.gb_classifier = GradientBoostingClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=5,
            learning_rate=0.1
        )
        self.label_encoder_type = LabelEncoder()
        self.label_encoder_priority = LabelEncoder()
        
        # Enhanced BNS section mapping
        self.bns_rules = {
            'murder': {
                'sections': ['Section 103 BNS', 'Section 101 BNS'],
                'keywords': ['murder', 'kill', 'homicide', 'death', 'killed', 'slain', 'assassination', 'fatal'],
                'weight': 0.95
            },
            'theft': {
                'sections': ['Section 303 BNS', 'Section 304 BNS'],
                'keywords': ['theft', 'steal', 'stolen', 'burglary', 'robbery', 'larceny', 'misappropriation', 'embezzlement'],
                'weight': 0.9
            },
            'assault': {
                'sections': ['Section 115 BNS', 'Section 117 BNS'],
                'keywords': ['assault', 'attack', 'violence', 'hurt', 'injury', 'beaten', 'physical harm', 'abuse'],
                'weight': 0.85
            },
            'fraud': {
                'sections': ['Section 318 BNS', 'Section 319 BNS'],
                'keywords': ['fraud', 'cheating', 'deception', 'forgery', 'scam', 'swindle', 'embezzle'],
                'weight': 0.9
            },
            'rape': {
                'sections': ['Section 63 BNS', 'Section 64 BNS'],
                'keywords': ['rape', 'sexual assault', 'molestation', 'sexual harassment', 'outraging modesty', 'sexual abuse'],
                'weight': 0.95
            },
            'kidnapping': {
                'sections': ['Section 137 BNS', 'Section 140 BNS'],
                'keywords': ['kidnapping', 'abduction', 'kidnap', 'missing person', 'forcible confinement', 'abduct'],
                'weight': 0.95
            },
            'drug': {
                'sections': ['Section 327 BNS', 'Section 328 BNS'],
                'keywords': ['drugs', 'narcotics', 'substance abuse', 'possession', 'trafficking', 'ganja', 'cocaine', 'heroin'],
                'weight': 0.9
            },
            'cybercrime': {
                'sections': ['Section 294 BNS', 'Section 295 BNS'],
                'keywords': ['cyber', 'computer', 'internet', 'online', 'digital', 'hacking', 'phishing', 'data theft'],
                'weight': 0.85
            },
            'corruption': {
                'sections': ['Section 290 BNS', 'Section 291 BNS'],
                'keywords': ['corruption', 'bribery', 'bribe', 'illegal gratification', 'public servant', 'graft'],
                'weight': 0.9
            },
            'dowry': {
                'sections': ['Section 85 BNS', 'Section 86 BNS'],
                'keywords': ['dowry', 'dowry death', 'dowry harassment', 'dowry demand', 'bride burning'],
                'weight': 0.95
            },
            'civil_property': {
                'sections': ['Civil Property Section 12', 'Civil Property Section 15'],
                'keywords': ['property', 'land', 'dispute', 'partition', 'ownership', 'inheritance', 'estate'],
                'weight': 0.8
            },
            'civil_contract': {
                'sections': ['Civil Contract Section 25', 'Civil Contract Section 30'],
                'keywords': ['contract', 'breach', 'agreement', 'violation', 'terms', 'conditions', 'commercial'],
                'weight': 0.8
            },
            'civil_family': {
                'sections': ['Family Law Section 40', 'Family Law Section 45'],
                'keywords': ['divorce', 'custody', 'maintenance', 'alimony', 'matrimonial', 'child support', 'separation'],
                'weight': 0.85
            }
        }
    
    def load_cases_from_db(self):
        """Load all cases from MongoDB database"""
        print("🔌 Connecting to MongoDB...")
        client = MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        cases_collection = db['cases']
        
        print("📊 Loading cases from database...")
        cases = list(cases_collection.find())
        print(f"✅ Loaded {len(cases)} cases from database")
        
        # Convert to DataFrame
        df = pd.DataFrame(cases)
        
        # Create combined text field for training
        df['full_text'] = df.apply(lambda row: 
            f"{row.get('title', '')} {row.get('description', '')} {row.get('case_type', '')} {row.get('filing_number', '')}", 
            axis=1
        )
        
        return df
    
    def rule_based_classification(self, text: str) -> dict:
        """Enhanced rule-based classification"""
        text_lower = text.lower()
        scores = {}
        
        for category, rules in self.bns_rules.items():
            score = 0
            matched_keywords = []
            
            for keyword in rules['keywords']:
                if keyword in text_lower:
                    score += rules['weight']
                    matched_keywords.append(keyword)
            
            if matched_keywords:
                # Normalize score
                normalized_score = min(score / len(rules['keywords']), 1.0)
                scores[category] = {
                    'score': normalized_score,
                    'keywords': matched_keywords,
                    'sections': rules['sections']
                }
        
        if scores:
            best_category = max(scores.keys(), key=lambda k: scores[k]['score'])
            return {
                'prediction': scores[best_category]['sections'][0],
                'confidence': scores[best_category]['score'],
                'matched_keywords': scores[best_category]['keywords'],
                'category': best_category
            }
        
        return {
            'prediction': 'Unclassified',
            'confidence': 0.2,
            'matched_keywords': [],
            'category': 'unknown'
        }
    
    def train_models(self, df: pd.DataFrame):
        """Train classification models"""
        
        print("\n🔬 Preparing training data...")
        
        # Prepare features and targets
        X = df['full_text'].values
        y_type = df['case_type'].values
        y_priority = df['priority'].values
        
        print(f"📚 Training samples: {len(X)}")
        print(f"📊 Case types: {np.unique(y_type)}")
        print(f"🚨 Priorities: {np.unique(y_priority)}")
        
        # Encode labels
        self.label_encoder_type.fit(y_type)
        self.label_encoder_priority.fit(y_priority)
        
        y_type_encoded = self.label_encoder_type.transform(y_type)
        y_priority_encoded = self.label_encoder_priority.transform(y_priority)
        
        # Split data
        X_train, X_test, y_type_train, y_type_test, y_priority_train, y_priority_test = train_test_split(
            X, y_type_encoded, y_priority_encoded, 
            test_size=0.2, 
            random_state=42,
            stratify=y_type_encoded
        )
        
        print(f"\n📈 Training set: {len(X_train)} samples")
        print(f"🧪 Test set: {len(X_test)} samples")
        
        # TF-IDF vectorization
        print("\n🔤 Vectorizing text...")
        X_train_tfidf = self.tfidf_vectorizer.fit_transform(X_train)
        X_test_tfidf = self.tfidf_vectorizer.transform(X_test)
        
        # Train case type classifier
        print("\n🎯 Training Case Type Classifier...")
        self.rf_classifier.fit(X_train_tfidf, y_type_train)
        
        # Train priority classifier
        print("🚨 Training Priority Classifier...")
        self.gb_classifier.fit(X_train_tfidf, y_priority_train)
        
        # Evaluate
        print("\n📊 Evaluating models...")
        
        # Case type predictions
        y_type_pred = self.rf_classifier.predict(X_test_tfidf)
        type_accuracy = accuracy_score(y_type_test, y_type_pred)
        
        # Priority predictions
        y_priority_pred = self.gb_classifier.predict(X_test_tfidf)
        priority_accuracy = accuracy_score(y_priority_test, y_priority_pred)
        
        # Cross-validation
        cv_scores_type = cross_val_score(self.rf_classifier, X_train_tfidf, y_type_train, cv=5)
        cv_scores_priority = cross_val_score(self.gb_classifier, X_train_tfidf, y_priority_train, cv=5)
        
        results = {
            'type_accuracy': type_accuracy,
            'priority_accuracy': priority_accuracy,
            'type_cv_mean': cv_scores_type.mean(),
            'type_cv_std': cv_scores_type.std(),
            'priority_cv_mean': cv_scores_priority.mean(),
            'priority_cv_std': cv_scores_priority.std(),
            'test_size': len(X_test),
            'train_size': len(X_train)
        }
        
        print(f"\n✨ Case Type Accuracy: {type_accuracy:.1%}")
        print(f"   Cross-validation: {cv_scores_type.mean():.1%} ± {cv_scores_type.std():.1%}")
        print(f"\n🚨 Priority Accuracy: {priority_accuracy:.1%}")
        print(f"   Cross-validation: {cv_scores_priority.mean():.1%} ± {cv_scores_priority.std():.1%}")
        
        # Detailed reports
        print(f"\n📋 Case Type Classification Report:")
        print(classification_report(
            self.label_encoder_type.inverse_transform(y_type_test),
            self.label_encoder_type.inverse_transform(y_type_pred)
        ))
        
        print(f"\n📋 Priority Classification Report:")
        print(classification_report(
            self.label_encoder_priority.inverse_transform(y_priority_test),
            self.label_encoder_priority.inverse_transform(y_priority_pred)
        ))
        
        return results
    
    def predict(self, case_description: str) -> dict:
        """Predict case type, priority, and BNS section"""
        
        # ML predictions
        tfidf_features = self.tfidf_vectorizer.transform([case_description])
        
        # Case type
        type_probs = self.rf_classifier.predict_proba(tfidf_features)[0]
        type_idx = np.argmax(type_probs)
        case_type = self.label_encoder_type.inverse_transform([type_idx])[0]
        type_confidence = float(type_probs[type_idx])
        
        # Priority
        priority_probs = self.gb_classifier.predict_proba(tfidf_features)[0]
        priority_idx = np.argmax(priority_probs)
        priority = self.label_encoder_priority.inverse_transform([priority_idx])[0]
        priority_confidence = float(priority_probs[priority_idx])
        
        # BNS section (rule-based)
        bns_result = self.rule_based_classification(case_description)
        
        return {
            'case_type': case_type,
            'case_type_confidence': type_confidence,
            'priority': priority,
            'priority_confidence': priority_confidence,
            'bns_section': bns_result['prediction'],
            'bns_confidence': bns_result['confidence'],
            'matched_keywords': bns_result['matched_keywords'],
            'overall_confidence': (type_confidence + priority_confidence + bns_result['confidence']) / 3
        }
    
    def save_model(self, filepath: str):
        """Save trained model"""
        model_data = {
            'model': self,  # Save the entire classifier for compatibility
            'vectorizer': self.tfidf_vectorizer,
            'tfidf_vectorizer': self.tfidf_vectorizer,
            'rf_classifier': self.rf_classifier,
            'gb_classifier': self.gb_classifier,
            'label_encoder_type': self.label_encoder_type,
            'label_encoder_priority': self.label_encoder_priority,
            'bns_rules': self.bns_rules
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"\n💾 Model saved to: {filepath}")

def main():
    """Main training pipeline"""
    print("=" * 70)
    print("🧠 ENHANCED BNS CLASSIFIER V2 - Training with Database Cases")
    print("=" * 70)
    
    # Initialize classifier
    classifier = EnhancedBNSClassifierV2()
    
    # Load cases from database
    df = classifier.load_cases_from_db()
    
    if len(df) < 10:
        print("❌ Not enough cases in database for training!")
        print("   Please run create_large_dataset.py first")
        return
    
    # Train models
    results = classifier.train_models(df)
    
    # Test predictions
    print("\n" + "=" * 70)
    print("🧪 TESTING PREDICTIONS")
    print("=" * 70)
    
    test_cases = [
        "Man murdered his business partner over financial dispute using knife",
        "Employee embezzled company funds worth 50 lakhs through fake invoices",
        "Domestic violence case with wife assaulted by husband demanding dowry",
        "Online fraud targeting elderly people through fake investment scheme",
        "Property dispute between brothers over ancestral land inheritance",
        "Child kidnapping for ransom by organized criminal gang",
        "Drug trafficking case with 20kg cocaine smuggled from abroad"
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case[:60]}...")
        result = classifier.predict(case)
        print(f"   📂 Case Type: {result['case_type']} ({result['case_type_confidence']:.1%})")
        print(f"   🚨 Priority: {result['priority']} ({result['priority_confidence']:.1%})")
        print(f"   ⚖️  BNS Section: {result['bns_section']} ({result['bns_confidence']:.1%})")
        print(f"   🎯 Overall Confidence: {result['overall_confidence']:.1%}")
        if result['matched_keywords']:
            print(f"   🔑 Keywords: {', '.join(result['matched_keywords'][:5])}")
    
    # Save model
    model_path = "models/enhanced_bns_model.pkl"
    classifier.save_model(model_path)
    
    # Save model info
    model_info = {
        "model_name": "Enhanced BNS Classifier V2",
        "training_date": datetime.now().isoformat(),
        "dataset_size": len(df),
        "case_types": df['case_type'].unique().tolist(),
        "priorities": df['priority'].unique().tolist(),
        "type_accuracy": results['type_accuracy'],
        "priority_accuracy": results['priority_accuracy'],
        "type_cv_score": results['type_cv_mean'],
        "priority_cv_score": results['priority_cv_mean'],
        "features": {
            "tfidf_features": 2000,
            "rf_estimators": 200,
            "gb_estimators": 100
        },
        "bns_rules": len(classifier.bns_rules)
    }
    
    with open("models/model_info.json", "w") as f:
        json.dump(model_info, f, indent=2)
    
    print("\n" + "=" * 70)
    print("✅ MODEL TRAINING COMPLETE!")
    print("=" * 70)
    print(f"📊 Dataset: {len(df)} cases")
    print(f"✨ Case Type Accuracy: {results['type_accuracy']:.1%}")
    print(f"🚨 Priority Accuracy: {results['priority_accuracy']:.1%}")
    print(f"⚖️  BNS Rules: {len(classifier.bns_rules)} categories")
    print("💾 Model files saved:")
    print(f"   - {model_path}")
    print(f"   - models/model_info.json")
    print("\n🚀 Model is ready for production use!")
    
    return classifier, results

if __name__ == "__main__":
    classifier, results = main()

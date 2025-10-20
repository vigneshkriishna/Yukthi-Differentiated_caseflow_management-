"""
BNS ML Model Trainer
Trains TF-IDF + Linear SVM classifier for BNS section prediction
"""
import pickle
import json
import os
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.pipeline import Pipeline
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# Import training data
from .bns_training_data import get_training_data, get_all_sections


class BNSModelTrainer:
    """Train ML models for BNS section classification"""
    
    def __init__(self, model_dir="./models"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            print("📦 Downloading NLTK data...")
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        
        # Model components
        self.vectorizer = None
        self.classifier = None
        self.pipeline = None
        self.label_encoder = {}
        self.reverse_label_encoder = {}
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for better feature extraction"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and stem
        processed_tokens = []
        for token in tokens:
            if token not in self.stop_words and len(token) > 2:
                stemmed = self.stemmer.stem(token)
                processed_tokens.append(stemmed)
        
        return ' '.join(processed_tokens)
    
    def prepare_training_data(self) -> Tuple[List[str], List[str]]:
        """Prepare training data from real datasets or fallback to synthetic"""
        import pandas as pd
        import json
        from pathlib import Path
        
        # Try to load real dataset first
        data_dir = Path("data/legal_datasets")
        processed_file = data_dir / "processed_legal_dataset.csv"
        
        if processed_file.exists():
            print("📋 Loading real legal dataset...")
            df = pd.read_csv(processed_file)
            texts = []
            labels = []
            
            for _, row in df.iterrows():
                processed_text = self.preprocess_text(row['text'])
                texts.append(processed_text)
                # Use first section if multiple sections
                label = str(row['labels']).split(',')[0].strip()
                labels.append(label)
            
            print(f"✅ Loaded {len(texts)} real cases with {len(set(labels))} unique sections")
            return texts, labels
        
        # Try manual curated dataset
        manual_file = data_dir / "manual_curated_cases.json"
        if manual_file.exists():
            print("📋 Loading manual curated dataset...")
            with open(manual_file, 'r', encoding='utf-8') as f:
                cases = json.load(f)
            
            texts = []
            labels = []
            
            for case in cases:
                processed_text = self.preprocess_text(case["facts"])
                texts.append(processed_text)
                labels.append(case["sections"][0])
            
            print(f"✅ Loaded {len(texts)} manual cases with {len(set(labels))} unique sections")
            return texts, labels
        
        # Fallback to synthetic BNS data
        print("📋 No real dataset found, using synthetic BNS data...")
        training_data = get_training_data()
        
        texts = []
        labels = []
        
        for section_data in training_data:
            section_number = section_data["section"]
            examples = section_data["examples"]
            
            for example in examples:
                processed_text = self.preprocess_text(example)
                texts.append(processed_text)
                labels.append(section_number)
        
        print(f"✅ Loaded {len(texts)} synthetic examples for {len(set(labels))} sections")
        return texts, labels
    
    def create_label_encoders(self, labels: List[str]):
        """Create label encoding mappings"""
        unique_labels = sorted(set(labels))
        self.label_encoder = {label: idx for idx, label in enumerate(unique_labels)}
        self.reverse_label_encoder = {idx: label for label, idx in self.label_encoder.items()}
        
        print(f"📊 Created encoders for {len(unique_labels)} unique sections")
    
    def train_model(self, test_size=0.2, random_state=42):
        """Train the BNS classification model"""
        print("🤖 Training BNS Classification Model...")
        
        # Prepare data
        texts, labels = self.prepare_training_data()
        self.create_label_encoders(labels)
        
        # Encode labels
        encoded_labels = [self.label_encoder[label] for label in labels]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            texts, encoded_labels, test_size=test_size, random_state=random_state, stratify=encoded_labels
        )
        
        print(f"📊 Training set: {len(X_train)} examples")
        print(f"📊 Test set: {len(X_test)} examples")
        
        # Create pipeline
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),  # Use unigrams and bigrams
                min_df=2,
                max_df=0.95,
                sublinear_tf=True
            )),
            ('classifier', LogisticRegression(
                max_iter=1000,
                random_state=random_state,
                class_weight='balanced'  # Handle class imbalance
            ))
        ])
        
        # Train the model
        print("🏋️ Training model...")
        self.pipeline.fit(X_train, y_train)
        
        # Evaluate model
        print("📈 Evaluating model...")
        y_pred = self.pipeline.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        print(f"✅ Model Accuracy: {accuracy:.4f}")
        
        # Cross-validation
        cv_scores = cross_val_score(self.pipeline, texts, encoded_labels, cv=5)
        print(f"✅ Cross-validation Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Detailed classification report
        print("\n📊 Classification Report:")
        target_names = [self.reverse_label_encoder[i] for i in range(len(self.reverse_label_encoder))]
        print(classification_report(y_test, y_pred, target_names=target_names))
        
        # Store model components
        self.vectorizer = self.pipeline.named_steps['tfidf']
        self.classifier = self.pipeline.named_steps['classifier']
        
        return accuracy, cv_scores
    
    def predict_section(self, case_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Predict BNS sections for given case text"""
        if self.pipeline is None:
            raise ValueError("Model not trained yet. Call train_model() first.")
        
        # Preprocess text
        processed_text = self.preprocess_text(case_text)
        
        # Get prediction probabilities
        probabilities = self.pipeline.predict_proba([processed_text])[0]
        
        # Get top-k predictions
        top_indices = np.argsort(probabilities)[::-1][:top_k]
        
        predictions = []
        for idx in top_indices:
            section_number = self.reverse_label_encoder[idx]
            confidence = probabilities[idx]
            
            # Get section details from training data
            training_data = get_training_data()
            section_details = next(
                (item for item in training_data if item["section"] == section_number), 
                None
            )
            
            prediction = {
                "section_number": section_number,
                "confidence": float(confidence),
                "title": section_details["title"] if section_details else "Unknown",
                "description": section_details["description"] if section_details else "No description available"
            }
            predictions.append(prediction)
        
        return predictions
    
    def save_model(self, filename_prefix="bns_model"):
        """Save trained model to disk"""
        if self.pipeline is None:
            raise ValueError("No model to save. Train model first.")
        
        model_path = os.path.join(self.model_dir, f"{filename_prefix}.pkl")
        encoders_path = os.path.join(self.model_dir, f"{filename_prefix}_encoders.json")
        
        # Save model pipeline
        with open(model_path, 'wb') as f:
            pickle.dump(self.pipeline, f)
        
        # Save encoders
        encoders_data = {
            "label_encoder": self.label_encoder,
            "reverse_label_encoder": self.reverse_label_encoder
        }
        with open(encoders_path, 'w') as f:
            json.dump(encoders_data, f, indent=2)
        
        print(f"✅ Model saved to {model_path}")
        print(f"✅ Encoders saved to {encoders_path}")
        
        return model_path, encoders_path
    
    def load_model(self, filename_prefix="bns_model"):
        """Load trained model from disk"""
        model_path = os.path.join(self.model_dir, f"{filename_prefix}.pkl")
        encoders_path = os.path.join(self.model_dir, f"{filename_prefix}_encoders.json")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Load model pipeline
        with open(model_path, 'rb') as f:
            self.pipeline = pickle.load(f)
        
        # Load encoders
        with open(encoders_path, 'r') as f:
            encoders_data = json.load(f)
            self.label_encoder = encoders_data["label_encoder"]
            self.reverse_label_encoder = {
                int(k): v for k, v in encoders_data["reverse_label_encoder"].items()
            }
        
        # Extract components
        self.vectorizer = self.pipeline.named_steps['tfidf']
        self.classifier = self.pipeline.named_steps['classifier']
        
        print(f"✅ Model loaded from {model_path}")
        return True
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the trained model"""
        if self.pipeline is None:
            return {"status": "No model trained"}
        
        return {
            "status": "Model trained",
            "num_sections": len(self.label_encoder),
            "sections_covered": list(self.label_encoder.keys()),
            "feature_count": self.vectorizer.get_feature_names_out().shape[0] if hasattr(self.vectorizer, 'get_feature_names_out') else "Unknown",
            "algorithm": "TF-IDF + Logistic Regression",
            "version": "1.0.0"
        }


def train_bns_model():
    """Main function to train BNS model"""
    print("🏛️ BNS Section Classification Model Training")
    print("=" * 50)
    
    trainer = BNSModelTrainer()
    
    # Train model
    accuracy, cv_scores = trainer.train_model()
    
    # Save model
    model_path, encoders_path = trainer.save_model()
    
    # Test with sample cases
    print("\n🧪 Testing model with sample cases:")
    test_cases = [
        "The accused committed murder by shooting the victim with a pistol",
        "Theft of mobile phone from pocket in crowded market place",
        "Online fraud scheme defrauding investors of lakhs of rupees",
        "Domestic violence and harassment by husband for dowry"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test Case {i}: {test_case}")
        predictions = trainer.predict_section(test_case, top_k=2)
        
        for j, pred in enumerate(predictions, 1):
            print(f"   {j}. Section {pred['section_number']}: {pred['title']} (Confidence: {pred['confidence']:.3f})")
    
    # Model info
    print(f"\n📊 Model Information:")
    info = trainer.get_model_info()
    for key, value in info.items():
        print(f"   • {key}: {value}")
    
    print(f"\n✅ BNS Model Training Complete!")
    print(f"📁 Model saved to: {model_path}")
    
    return trainer


if __name__ == "__main__":
    trainer = train_bns_model()

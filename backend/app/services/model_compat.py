"""
Model Compatibility Layer
This module provides backward compatibility for loading legacy pickled models
"""

import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder


class EnhancedBNSClassifierV2:
    """
    Compatibility class for loading legacy EnhancedBNSClassifierV2 models
    This matches the structure from train_with_database_cases.py
    """

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

    def rule_based_classification(self, text: str) -> dict:
        """Enhanced rule-based classification"""
        text_lower = text.lower()
        matches = []
        best_match = None
        best_weight = 0

        for category, data in self.bns_rules.items():
            keyword_count = sum(1 for keyword in data['keywords'] if keyword in text_lower)
            if keyword_count > 0:
                confidence = min((keyword_count / len(data['keywords'])) * data['weight'], 1.0)
                matches.append({
                    'category': category,
                    'sections': data['sections'],
                    'confidence': confidence,
                    'keywords_matched': keyword_count
                })
                if confidence > best_weight:
                    best_weight = confidence
                    best_match = data['sections'][0]

        return {
            'predicted_section': best_match if best_match else 'General Section',
            'confidence': best_weight if best_weight > 0 else 0.3,
            'all_matches': matches
        }

    def predict(self, text: str) -> dict:
        """Predict BNS section for given case text"""
        # Use rule-based classification as fallback
        return self.rule_based_classification(text)


# Register the class in __main__ module for pickle compatibility
sys.modules['__main__'].EnhancedBNSClassifierV2 = EnhancedBNSClassifierV2

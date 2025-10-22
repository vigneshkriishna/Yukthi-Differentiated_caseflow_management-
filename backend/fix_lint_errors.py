#!/usr/bin/env python3
"""
Automated script to fix remaining Ruff linting errors
"""
import re
from pathlib import Path

def fix_file(filepath, fixes):
    """Apply fixes to a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Fixed: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"✗ Error in {filepath}: {e}")
        return False

# Define fixes for each file
fixes_map = {
    "app/services/dcm_rules.py": [
        (r'^import re\n', ''),
        (r'^import json\n', ''),
    ],
    "app/services/email_service.py": [
        (r'from typing import Dict, List, Optional', 'from typing import Dict, List'),
        (r'from datetime import datetime, date', 'from datetime import datetime'),
    ],
    "app/services/enhanced_nlp_service.py": [
        (r'from typing import Dict, List, Optional', 'from typing import Dict, List'),
        (r'f"BNS Classification Service initialized"', '"BNS Classification Service initialized"'),
        (r'f"Using model: ensemble"', '"Using model: ensemble"'),
    ],
    "app/services/nlp/bns_assist.py": [
        (r'^import json\n', ''),
        (r'from pathlib import Path', ''),
        (r'synopsis_lower = synopsis\.lower\(\)', '# synopsis_lower = synopsis.lower()  # Unused'),
    ],
    "app/services/nlp/bns_ensemble_model.py": [
        (r'import pandas as pd', '# import pandas as pd  # Unused'),
        (r'from sklearn\.metrics import.*confusion_matrix', 'from sklearn.metrics import classification_report, accuracy_score'),
        (r'y_pred_proba = ', '# y_pred_proba =  # Unused variable\n            _ = '),
        (r'f"\\nModel successfully saved"', '"\\nModel successfully saved"'),
        (r'training_results = ', '# training_results =  # Unused variable\n        _ = '),
        (r'f"\\nTraining complete!"', '"\\nTraining complete!"'),
        (r'f"\\nBest model saved"', '"\\nBest model saved"'),
    ],
    "app/services/nlp/bns_model_trainer.py": [
        (r'from sklearn\.metrics import.*confusion_matrix', 'from sklearn.metrics import classification_report, accuracy_score'),
        (r'from \.bns_training_data import.*get_all_sections', 'from .bns_training_data import BNS_SECTIONS'),
        (r'f"Model and vectorizer saved"', '"Model and vectorizer saved"'),
        (r'f"Training complete!"', '"Training complete!"'),
    ],
    "app/services/nlp/bns_training_data.py": [
        (r'f"Total sections: "', '"Total sections: "'),
    ],
    "app/services/nlp/enhanced_bns_service.py": [
        (r'^import os\n', ''),
        (r'^import json\n', ''),
        (r'from pathlib import Path', ''),
        (r'from \.bns_training_data import.*get_section_details', 'from .bns_training_data import BNS_SECTIONS'),
        (r'^def get_section_details.*?(?=\n\nclass|\Z)', '', re.DOTALL),
        (r'f"Enhanced BNS Service initialized"', '"Enhanced BNS Service initialized"'),
    ],
    "app/services/scheduler.py": [
        (r'from datetime import date, time, datetime', 'from datetime import date, time'),
    ],
    "app/services/simple_smart_scheduling.py": [
        (r'from typing import List, Dict, Optional', 'from typing import List, Dict'),
        (r'from datetime import datetime, timedelta, date', 'from datetime import datetime, timedelta'),
        (r'from app\.models\.case import Case, CasePriority, CaseType', 'from app.models.case import Case, CasePriority'),
        (r'User\.is_active == True', 'User.is_active'),
    ],
    "app/services/smart_scheduling_service.py": [
        (r'from typing import List, Dict, Optional, Tuple', 'from typing import List, Dict, Optional'),
        (r'from app\.models\.user import User, UserRole', 'from app.models.user import UserRole'),
        (r'case_duration = ', '# case_duration =  # Unused variable\n        _ = '),
    ],
    "app/services/sms_service.py": [
        (r'from typing import Dict, List, Optional', 'from typing import Dict, List'),
    ],
}

# Fix all files
fixed_count = 0
for filepath, fixes in fixes_map.items():
    full_path = Path(__file__).parent / filepath
    if full_path.exists():
        if fix_file(full_path, fixes):
            fixed_count += 1

print(f"\n✓ Fixed {fixed_count} files")

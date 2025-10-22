"""
Router initialization
"""
from . import auth, cases, nlp, reports, schedule

__all__ = [
    "auth",
    "cases",
    "schedule",
    "reports",
    "nlp"
]

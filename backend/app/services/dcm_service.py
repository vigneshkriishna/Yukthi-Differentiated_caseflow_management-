"""
DCM Service alias for backward compatibility
"""
from .dcm_rules import DCMRulesEngine as DCMService

__all__ = ["DCMService"]

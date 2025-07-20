"""
MOHU - Multi-Objective Homophone Understanding

A fuzzy string matching library with pinyin and character-based strategies.
"""

from .matcher import MohuMatcher

__version__ = "0.1.0"
__author__ = "MOHU Contributors"
__description__ = "A fuzzy string matching library with pinyin and character-based strategies"

# Make MohuMatcher available at package level
__all__ = ["MohuMatcher"]

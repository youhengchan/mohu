"""
This module contains the default configurations and constants for the PyMOHU library.
"""
from pathlib import Path

# --- Paths ---
# Base directory of the package
_BASE_DIR = Path(__file__).parent.resolve()

# Path to the data directory
_DATA_DIR = _BASE_DIR / "data"

# Default paths to confusion data files
DEFAULT_PINYIN_CONFUSION_PATH = _DATA_DIR / "pinyin_confusion.json"
DEFAULT_CHAR_CONFUSION_PATH = _DATA_DIR / "char_confusion.json"


# --- Default Matching Parameters ---

# The minimum similarity score for a candidate to be considered a match.
# Value should be between 0.0 and 1.0.
DEFAULT_SIMILARITY_THRESHOLD = 0.7

# The maximum edit distance for the fuzzy search in the AC automaton.
# A higher value increases recall but may decrease performance.
DEFAULT_MAX_DISTANCE = 2

# Whether to ignore tones (e.g., 'ā' -> 'a') in pinyin matching.
# Ignoring tones generally improves recall for most use cases.
DEFAULT_IGNORE_TONES = True


# --- Hybrid Mode Configuration ---

# Default weights for combining pinyin and char scores in hybrid mode.
# The scores are weighted and summed up. They don't have to sum to 1.
DEFAULT_HYBRID_WEIGHTS = {
    "pinyin": 0.5,
    "char": 0.5,
} 
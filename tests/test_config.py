"""
Tests for the configuration module.
"""
import os
from pathlib import Path

import pytest
from mohu import config


def test_constants_existence_and_types():
    """
    Test if all required constants exist in the config module and have the correct types.
    """
    assert hasattr(config, "DEFAULT_SIMILARITY_THRESHOLD")
    assert isinstance(config.DEFAULT_SIMILARITY_THRESHOLD, float)

    assert hasattr(config, "DEFAULT_MAX_DISTANCE")
    assert isinstance(config.DEFAULT_MAX_DISTANCE, int)

    assert hasattr(config, "DEFAULT_IGNORE_TONES")
    assert isinstance(config.DEFAULT_IGNORE_TONES, bool)

    assert hasattr(config, "DEFAULT_HYBRID_WEIGHTS")
    assert isinstance(config.DEFAULT_HYBRID_WEIGHTS, dict)
    assert "pinyin" in config.DEFAULT_HYBRID_WEIGHTS
    assert "char" in config.DEFAULT_HYBRID_WEIGHTS
    assert isinstance(config.DEFAULT_HYBRID_WEIGHTS["pinyin"], float)
    assert isinstance(config.DEFAULT_HYBRID_WEIGHTS["char"], float)


def test_data_file_paths_existence():
    """
    Test if the default data file paths are defined and point to existing files.
    """
    assert hasattr(config, "DEFAULT_PINYIN_CONFUSION_PATH")
    assert isinstance(config.DEFAULT_PINYIN_CONFUSION_PATH, Path)
    assert os.path.exists(config.DEFAULT_PINYIN_CONFUSION_PATH), \
        f"Pinyin confusion file not found at: {config.DEFAULT_PINYIN_CONFUSION_PATH}"

    assert hasattr(config, "DEFAULT_CHAR_CONFUSION_PATH")
    assert isinstance(config.DEFAULT_CHAR_CONFUSION_PATH, Path)
    assert os.path.exists(config.DEFAULT_CHAR_CONFUSION_PATH), \
        f"Character confusion file not found at: {config.DEFAULT_CHAR_CONFUSION_PATH}"

def test_data_paths_are_absolute():
    """
    Test if the file paths are absolute, which is important for robustness.
    """
    assert config.DEFAULT_PINYIN_CONFUSION_PATH.is_absolute()
    assert config.DEFAULT_CHAR_CONFUSION_PATH.is_absolute() 
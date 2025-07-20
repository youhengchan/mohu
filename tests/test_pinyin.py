"""
Tests for the PinyinConverter class.
"""
import pytest
from mohu.pinyin import PinyinConverter

# Test cases for PinyinConverter
# Format: (word, ignore_tones, expected_pinyin_list)
TEST_CASES = [
    # --- Basic Cases ---
    ("北京", False, ["běi", "jīng"]),
    ("北京", True, ["bei", "jing"]),
    ("重庆", False, ["chóng", "qìng"]),
    ("重庆", True, ["chong", "qing"]),
    
    # --- Mixed Characters ---
    ("hello世界", False, ["hello", "shì", "jiè"]),
    ("hello世界", True, ["hello", "shi", "jie"]),
    ("PyMOHU-v1", True, ["PyMOHU-v1"]),

    # --- Edge Cases ---
    ("", False, []),
    ("", True, []),
    
    # --- Punctuation ---
    ("你好，世界", False, ["nǐ", "hǎo", "，", "shì", "jiè"]),
    ("你好，世界", True, ["ni", "hao", "，", "shi", "jie"]),
    
    # --- Polyphonic characters ---
    # '行' can be 'háng' or 'xíng'
    ("银行", False, ["yín", "háng"]),
    ("行为", False, ["xíng", "wéi"]),
]

@pytest.fixture(scope="module")
def converter():
    """
    Pytest fixture to provide a single instance of PinyinConverter for all tests in this module.
    """
    return PinyinConverter()

@pytest.mark.parametrize(
    "word, ignore_tones, expected_pinyin_list", TEST_CASES
)
def test_pinyin_conversion(converter, word, ignore_tones, expected_pinyin_list):
    """
    Tests the PinyinConverter with various inputs.
    """
    result = converter.convert(word, ignore_tones=ignore_tones)
    assert result == expected_pinyin_list

def test_converter_instance():
    """
    Test that the fixture returns a valid instance of PinyinConverter.
    """
    assert isinstance(PinyinConverter(), PinyinConverter) 
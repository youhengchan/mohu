"""
Tests for romanized pinyin input functionality in MohuMatcher.
"""
import pytest
from mohu import MohuMatcher
from mohu.pinyin import PinyinConverter


class TestRomanizedPinyinInput:
    """Test cases for romanized pinyin input functionality."""

    def test_pinyin_converter_split_basic(self):
        """Test basic pinyin string splitting functionality."""
        converter = PinyinConverter()
        
        # Test basic pinyin splitting
        result = converter.convert("pingguo")
        assert result == ["ping", "guo"], f"Expected ['ping', 'guo'], got {result}"
        
        # Test other common pinyin combinations
        result = converter.convert("beijing")
        assert result == ["bei", "jing"], f"Expected ['bei', 'jing'], got {result}"
        
        result = converter.convert("shanghai")
        assert result == ["shang", "hai"], f"Expected ['shang', 'hai'], got {result}"

    def test_pinyin_converter_handles_chinese(self):
        """Test that pinyin converter still handles Chinese characters correctly."""
        converter = PinyinConverter()
        
        # Test Chinese character conversion
        result = converter.convert("苹果")
        expected = ["píng", "guǒ"]  # With tones
        assert result == expected, f"Expected {expected}, got {result}"
        
        # Test Chinese character conversion without tones
        result = converter.convert("苹果", ignore_tones=True)
        expected = ["ping", "guo"]  # Without tones
        assert result == expected, f"Expected {expected}, got {result}"

    def test_pinyin_converter_mixed_input(self):
        """Test pinyin converter with mixed Chinese and English input."""
        converter = PinyinConverter()
        
        # Test mixed input (Chinese characters and numbers/letters)
        result = converter.convert("北京2024")
        # pypinyin should handle this gracefully
        assert len(result) > 0, "Should return some result for mixed input"

    def test_matcher_pinyin_mode_basic(self):
        """Test basic pinyin matching functionality."""
        matcher = MohuMatcher(ignore_tones=True)
        words = ["苹果", "香蕉", "橘子", "apple", "banana", "orange"]
        matcher.build(words)
        
        # Test pinyin matching for "苹果" using "pingguo"
        results = matcher.match("pingguo", mode='pinyin')
        
        # Should find "苹果" as the best match
        assert len(results) > 0, "Should find at least one match"
        assert results[0][0] == "苹果", f"Expected '苹果' as top match, got {results[0][0]}"
        assert results[0][1] == 1.0, f"Expected perfect match (1.0), got {results[0][1]}"

    def test_matcher_pinyin_mode_partial_match(self):
        """Test pinyin matching with partial matches."""
        matcher = MohuMatcher(ignore_tones=True, max_distance=2)
        words = ["苹果", "苹果汁", "苹果派", "柠檬"]
        matcher.build(words)
        
        # Test partial pinyin matching
        results = matcher.match("ping", mode='pinyin')
        
        # Should find words containing "ping"
        assert len(results) > 0, "Should find matches for partial pinyin"
        
        # Check that results contain words with "ping" sound
        found_words = [result[0] for result in results]
        assert "苹果" in found_words, "Should find '苹果' for 'ping' input"

    def test_matcher_pinyin_mode_fuzzy_match(self):
        """Test pinyin matching with fuzzy/approximate matches."""
        matcher = MohuMatcher(ignore_tones=True, max_distance=2)
        words = ["苹果", "香蕉", "橘子", "柠檬"]
        matcher.build(words)
        
        # Test approximate pinyin matching (with small typos)
        results = matcher.match("pinggou", mode='pinyin')  # "pinggou" instead of "pingguo"
        
        # Should still find "苹果" but with lower similarity
        assert len(results) > 0, "Should find approximate matches"
        top_match = results[0]
        assert top_match[0] == "苹果", f"Expected '苹果' as top match, got {top_match[0]}"
        assert top_match[1] >= 0.5, f"Expected reasonable similarity, got {top_match[1]}"

    def test_matcher_hybrid_mode_with_pinyin(self):
        """Test hybrid mode combining character and pinyin matching."""
        matcher = MohuMatcher(ignore_tones=True)
        words = ["苹果", "香蕉", "橘子", "apple", "banana", "orange"]
        matcher.build(words)
        
        # Test hybrid matching with pinyin input
        results = matcher.match("pingguo", mode='hybrid')
        
        # Should find "苹果" as the best match
        assert len(results) > 0, "Should find matches in hybrid mode"
        assert results[0][0] == "苹果", f"Expected '苹果' as top match, got {results[0][0]}"
        assert results[0][1] >= 0.4, f"Expected reasonable similarity in hybrid mode, got {results[0][1]}"

    def test_matcher_char_mode_vs_pinyin_mode(self):
        """Test comparing character mode vs pinyin mode results."""
        matcher = MohuMatcher(ignore_tones=True)
        words = ["苹果", "香蕉", "橘子"]
        matcher.build(words)
        
        # Test character mode with Chinese input
        char_results = matcher.match("苹", mode='char', max_results=3)
        
        # Test pinyin mode with romanized input
        pinyin_results = matcher.match("pingguo", mode='pinyin', max_results=3)
        
        # Both should find "苹果" but through different mechanisms
        assert len(char_results) > 0, "Character mode should find matches"
        assert len(pinyin_results) > 0, "Pinyin mode should find matches"
        
        # Pinyin mode should give perfect match for "pingguo" -> "苹果"
        assert pinyin_results[0][0] == "苹果", "Pinyin mode should find exact match"
        assert pinyin_results[0][1] == 1.0, "Pinyin mode should give perfect similarity"

    def test_matcher_with_filtering(self):
        """Test pinyin matching with similarity threshold and max results filtering."""
        matcher = MohuMatcher(ignore_tones=True)
        words = ["苹果", "香蕉", "橘子", "葡萄", "柠檬"]
        matcher.build(words)
        
        # Test with similarity threshold
        results = matcher.match(
            "pingguo", 
            mode='pinyin',
            similarity_threshold=0.7,  # Only return results with similarity >= 0.7
            max_results=3             # Max 3 results
        )
        
        # Should find high-quality matches only
        assert len(results) <= 3, "Should respect max_results limit"
        for word, similarity in results:
            assert similarity >= 0.7, f"All results should meet threshold, got {similarity} for {word}"
        
        # Should definitely include "苹果" with high similarity
        found_words = [result[0] for result in results]
        assert "苹果" in found_words, "Should find '苹果' for 'pingguo'"

    def test_matcher_empty_and_edge_cases(self):
        """Test edge cases for pinyin matching."""
        matcher = MohuMatcher(ignore_tones=True)
        words = ["苹果", "香蕉"]
        matcher.build(words)
        
        # Test empty input
        results = matcher.match("", mode='pinyin')
        assert results == [], "Empty input should return empty results"
        
        # Test non-pinyin input
        results = matcher.match("123", mode='pinyin')
        # Should handle gracefully (might return empty or convert as-is)
        assert isinstance(results, list), "Should return list for non-pinyin input"
        
        # Test very long pinyin string
        results = matcher.match("pingguo" * 10, mode='pinyin')
        assert isinstance(results, list), "Should handle long pinyin strings"

    def test_matcher_common_pinyin_words(self):
        """Test matching with common Chinese words using pinyin."""
        matcher = MohuMatcher(ignore_tones=True)
        words = ["北京", "上海", "广州", "深圳", "苹果", "香蕉"]
        matcher.build(words)
        
        test_cases = [
            ("beijing", "北京"),
            ("shanghai", "上海"), 
            ("guangzhou", "广州"),
            ("shenzhen", "深圳"),
            ("pingguo", "苹果"),
            ("xiangjiao", "香蕉")
        ]
        
        for pinyin_input, expected_word in test_cases:
            results = matcher.match(pinyin_input, mode='pinyin')
            assert len(results) > 0, f"Should find match for {pinyin_input}"
            assert results[0][0] == expected_word, f"Expected {expected_word} for {pinyin_input}, got {results[0][0]}"
            assert results[0][1] >= 0.8, f"Expected high similarity for {pinyin_input} -> {expected_word}"


def test_integration_roma_pinyin_workflow():
    """Integration test for the complete romanized pinyin workflow."""
    # Create matcher with configurations suitable for pinyin input
    matcher = MohuMatcher(
        max_distance=3,
        ignore_tones=True,
        similarity_threshold=0.0  # Set to 0 to see all matches
    )
    
    # Build with mixed Chinese and English words
    words = ["苹果", "香蕉", "橘子", "apple", "banana", "orange", "北京", "上海"]
    matcher.build(words)
    
    # Verify dictionary is built correctly
    assert matcher.get_word_count() == len(words)
    assert set(matcher.get_words()) == set(words)
    
    # Test various matching modes
    test_cases = [
        # (input, mode, expected_top_match, min_similarity)
        ("pingguo", "pinyin", "苹果", 0.9),
        ("苹", "char", "苹果", 0.4),
        ("苹果", "hybrid", "苹果", 0.9),
        ("beijing", "pinyin", "北京", 0.9),
        ("apple", "char", "apple", 0.9),
    ]
    
    for test_input, mode, expected_match, min_sim in test_cases:
        results = matcher.match(test_input, mode=mode)
        assert len(results) > 0, f"Should find matches for '{test_input}' in {mode} mode"
        assert results[0][0] == expected_match, f"Expected '{expected_match}' for '{test_input}', got '{results[0][0]}'"
        assert results[0][1] >= min_sim, f"Expected similarity >= {min_sim} for '{test_input}', got {results[0][1]}" 
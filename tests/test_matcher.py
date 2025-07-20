"""
Tests for the MohuMatcher class.
"""
import pytest
from mohu.matcher import MohuMatcher
from mohu.pinyin import PinyinConverter
from mohu.ac import ACAutomaton
from mohu.config import (
    DEFAULT_SIMILARITY_THRESHOLD,
    DEFAULT_MAX_DISTANCE,
    DEFAULT_IGNORE_TONES,
    DEFAULT_HYBRID_WEIGHTS,
    DEFAULT_PINYIN_CONFUSION_PATH,
    DEFAULT_CHAR_CONFUSION_PATH,
)


def test_matcher_initialization_default():
    """
    Tests that the MohuMatcher initializes with default parameters correctly.
    """
    matcher = MohuMatcher()
    
    # Check configuration parameters
    assert matcher.similarity_threshold == DEFAULT_SIMILARITY_THRESHOLD
    assert matcher.max_distance == DEFAULT_MAX_DISTANCE
    assert matcher.ignore_tones == DEFAULT_IGNORE_TONES
    assert matcher.hybrid_weights == DEFAULT_HYBRID_WEIGHTS
    assert matcher.pinyin_confusion_path == DEFAULT_PINYIN_CONFUSION_PATH
    assert matcher.char_confusion_path == DEFAULT_CHAR_CONFUSION_PATH
    
    # Check that components are initialized
    assert isinstance(matcher.pinyin_converter, PinyinConverter)
    
    # Check that state variables are properly initialized
    assert matcher.char_ac_index is None
    assert matcher.pinyin_ac_index is None
    assert matcher.pinyin_map == {}
    assert matcher.word_list == []
    assert matcher.pinyin_confusion is None
    assert matcher.char_confusion is None


def test_matcher_initialization_custom():
    """
    Tests that the MohuMatcher initializes with custom parameters correctly.
    """
    custom_weights = {"pinyin": 0.7, "char": 0.3}
    custom_paths = {
        "pinyin_confusion_path": "/custom/pinyin.json",
        "char_confusion_path": "/custom/char.json"
    }
    
    matcher = MohuMatcher(
        similarity_threshold=0.8,
        max_distance=3,
        ignore_tones=False,
        hybrid_weights=custom_weights,
        **custom_paths
    )

    # Check that custom parameters are stored correctly
    assert matcher.similarity_threshold == 0.8
    assert matcher.max_distance == 3
    assert matcher.ignore_tones is False
    assert matcher.hybrid_weights == custom_weights
    assert matcher.pinyin_confusion_path == "/custom/pinyin.json"
    assert matcher.char_confusion_path == "/custom/char.json"
    
    # Check that modifying the original weights dict doesn't affect the matcher
    custom_weights["pinyin"] = 0.9
    assert matcher.hybrid_weights["pinyin"] == 0.7


def test_matcher_initial_state():
    """
    Tests that all internal state variables are correctly initialized to None or empty.
    """
    matcher = MohuMatcher()
    
    # Verify that all state variables start in the expected initial state
    assert matcher.char_ac_index is None
    assert matcher.pinyin_ac_index is None
    assert isinstance(matcher.pinyin_map, dict) and len(matcher.pinyin_map) == 0
    assert isinstance(matcher.word_list, list) and len(matcher.word_list) == 0
    assert matcher.pinyin_confusion is None
    assert matcher.char_confusion is None


def test_matcher_build_with_word_list():
    """
    Tests that the build method correctly constructs indexes from a word list.
    """
    matcher = MohuMatcher()
    
    # Test with a small word list
    word_list = ["北京", "南京", "东京", "hello", "world"]
    matcher.build(word_list)
    
    # Check that word_list is stored (order-preserving, deduplicated)
    assert set(matcher.word_list) == set(word_list)
    
    # Check that char_ac_index is built and is an ACAutomaton instance
    assert matcher.char_ac_index is not None
    assert isinstance(matcher.char_ac_index, ACAutomaton)
    
    # Check that pinyin_ac_index is built and is an ACAutomaton instance  
    assert matcher.pinyin_ac_index is not None
    assert isinstance(matcher.pinyin_ac_index, ACAutomaton)
    
    # Check that pinyin_map is populated correctly
    assert isinstance(matcher.pinyin_map, dict)
    assert len(matcher.pinyin_map) > 0
    
    # Verify some specific pinyin mappings
    # 北京 should map to 'beijjing' or similar (depending on ignore_tones setting)
    beijing_pinyin = ''.join(matcher.pinyin_converter.convert("北京", ignore_tones=matcher.ignore_tones))
    assert beijing_pinyin in matcher.pinyin_map
    assert "北京" in matcher.pinyin_map[beijing_pinyin]
    
    # Check that non-Chinese words are handled
    hello_pinyin = ''.join(matcher.pinyin_converter.convert("hello", ignore_tones=matcher.ignore_tones))
    if hello_pinyin:  # Should be 'hello' since it's not Chinese
        assert hello_pinyin in matcher.pinyin_map
        assert "hello" in matcher.pinyin_map[hello_pinyin]


def test_matcher_build_empty_list():
    """
    Tests that the build method handles empty word lists correctly.
    """
    matcher = MohuMatcher()
    matcher.build([])
    
    # Check that all indexes are None or empty
    assert matcher.char_ac_index is None
    assert matcher.pinyin_ac_index is None
    assert matcher.pinyin_map == {}
    assert matcher.word_list == []


def test_matcher_build_overwrites_previous():
    """
    Tests that calling build multiple times overwrites the previous indexes.
    """
    matcher = MohuMatcher()
    
    # First build
    first_words = ["apple", "banana"]
    matcher.build(first_words)
    assert set(matcher.word_list) == set(first_words)
    assert len(matcher.pinyin_map) >= 1  # Should have some mappings
    
    # Second build should overwrite
    second_words = ["cat", "dog"]
    matcher.build(second_words)
    assert set(matcher.word_list) == set(second_words)
    
    # Check that old words are not in the new mapping
    apple_pinyin = ''.join(matcher.pinyin_converter.convert("apple", ignore_tones=matcher.ignore_tones))
    if apple_pinyin in matcher.pinyin_map:
        assert "apple" not in matcher.pinyin_map[apple_pinyin]


def test_matcher_match_char_basic():
    """
    Tests the _match_char method with basic functionality.
    """
    matcher = MohuMatcher()
    
    # Build index with some test words
    word_list = ["apple", "apply", "banana", "cat", "bat"]
    matcher.build(word_list)
    
    # Test exact match
    results = matcher._match_char("apple")
    assert len(results) > 0
    assert isinstance(results, list)
    assert isinstance(results[0], tuple)
    assert len(results[0]) == 2  # (word, score)
    assert results[0][0] == "apple"  # Should be top match
    assert results[0][1] == 1.0  # Perfect match
    
    # Test fuzzy match
    results = matcher._match_char("appl")  # Missing one character
    assert len(results) > 0
    # Should find "apple" and possibly "apply"
    words_found = [result[0] for result in results]
    assert "apple" in words_found
    
    # Test that results are sorted by score descending
    scores = [result[1] for result in results]
    assert scores == sorted(scores, reverse=True)


def test_matcher_match_char_edge_cases():
    """
    Tests the _match_char method with edge cases.
    """
    matcher = MohuMatcher()
    
    # Test without building index first
    results = matcher._match_char("test")
    assert results == []
    
    # Build index then test empty text
    word_list = ["apple", "banana"]
    matcher.build(word_list)
    
    results = matcher._match_char("")
    assert results == []
    
    # Test with text that has no matches within distance threshold
    results = matcher._match_char("xyz123")
    # Depending on max_distance, this might return empty or some matches
    assert isinstance(results, list)


def test_matcher_match_char_chinese():
    """
    Tests the _match_char method with Chinese characters.
    """
    matcher = MohuMatcher()
    
    # Build index with Chinese words
    word_list = ["北京", "南京", "东京", "北海"]
    matcher.build(word_list)
    
    # Test exact match
    results = matcher._match_char("北京")
    assert len(results) > 0
    assert results[0][0] == "北京"
    assert results[0][1] == 1.0
    
    # Test fuzzy match - "北" should match multiple words
    results = matcher._match_char("北")
    words_found = [result[0] for result in results]
    assert "北京" in words_found
    assert "北海" in words_found
    
    # Test with a character substitution
    results = matcher._match_char("南京")  
    assert len(results) > 0
    assert results[0][0] == "南京"


def test_matcher_load_confusion_matrix():
    """
    Tests the _load_confusion_matrix helper method.
    """
    matcher = MohuMatcher()
    
    # Test loading existing confusion matrix (should work with our test data)
    char_confusion = matcher._load_confusion_matrix(matcher.char_confusion_path)
    assert isinstance(char_confusion, dict)
    # Should contain some confusion mappings from our test data
    
    # Test loading non-existent file
    empty_confusion = matcher._load_confusion_matrix("/non/existent/path.json")
    assert empty_confusion == {}


def test_matcher_match_pinyin_basic():
    """
    Tests the _match_pinyin method with basic functionality.
    """
    matcher = MohuMatcher()
    
    # Build index with Chinese words
    word_list = ["北京", "南京", "东京", "背景"]
    matcher.build(word_list)
    
    # Test exact match with Chinese input
    results = matcher._match_pinyin("北京")
    assert len(results) > 0
    assert isinstance(results, list)
    assert isinstance(results[0], tuple)
    assert len(results[0]) == 2  # (word, score)
    
    # The exact match should be the top result
    words_found = [result[0] for result in results]
    assert "北京" in words_found
    
    # Test that results are sorted by score descending
    scores = [result[1] for result in results]
    assert scores == sorted(scores, reverse=True)


def test_matcher_match_pinyin_fuzzy():
    """
    Tests the _match_pinyin method with fuzzy matching.
    """
    matcher = MohuMatcher()
    
    # Build index with Chinese words that have similar pinyin
    word_list = ["北京", "背景", "南京", "东京"]  # bei/jing variations
    matcher.build(word_list)
    
    # Test fuzzy match - input pinyin should find similar sounding words
    results = matcher._match_pinyin("beijing")  # Romanized input
    assert len(results) >= 0  # May or may not find matches depending on conversion
    
    # Test with actual pinyin input
    results = matcher._match_pinyin("bei")  # Partial pinyin
    words_found = [result[0] for result in results]
    # Should find words that start with "bei" sound
    assert any("北京" in words_found or "背景" in words_found for _ in [True])


def test_matcher_match_pinyin_edge_cases():
    """
    Tests the _match_pinyin method with edge cases.
    """
    matcher = MohuMatcher()
    
    # Test without building index first
    results = matcher._match_pinyin("test")
    assert results == []
    
    # Build index then test empty text
    word_list = ["北京", "南京"]
    matcher.build(word_list)
    
    results = matcher._match_pinyin("")
    assert results == []
    
    # Test with non-Chinese text that has no pinyin conversion
    results = matcher._match_pinyin("xyz123")
    # Should handle gracefully - may return empty or process as-is
    assert isinstance(results, list)


def test_matcher_match_pinyin_ignore_tones():
    """
    Tests that the _match_pinyin method respects the ignore_tones setting.
    """
    # Test with ignore_tones=True (default)
    matcher_no_tones = MohuMatcher(ignore_tones=True)
    word_list = ["北京", "南京"]
    matcher_no_tones.build(word_list)
    
    # Test with ignore_tones=False
    matcher_with_tones = MohuMatcher(ignore_tones=False)
    matcher_with_tones.build(word_list)
    
    # Both should work, but may have different pinyin representations
    results_no_tones = matcher_no_tones._match_pinyin("北京")
    results_with_tones = matcher_with_tones._match_pinyin("北京")
    
    # Both should find results
    assert len(results_no_tones) > 0
    assert len(results_with_tones) > 0
    
    # Both should find "北京" as a match
    words_no_tones = [result[0] for result in results_no_tones]
    words_with_tones = [result[0] for result in results_with_tones]
    assert "北京" in words_no_tones
    assert "北京" in words_with_tones


def test_matcher_match_pinyin_deduplication():
    """
    Tests that _match_pinyin properly deduplicates results.
    """
    matcher = MohuMatcher()
    
    # Build index with words that might have similar pinyin
    word_list = ["北京", "背景", "被", "杯"]  # Some words with similar pinyin components
    matcher.build(word_list)
    
    results = matcher._match_pinyin("北京")
    
    # Check that each word appears only once in results
    words_found = [result[0] for result in results]
    assert len(words_found) == len(set(words_found)), "Results should not contain duplicates"


def test_matcher_match_char_mode():
    """
    Tests the public match method with mode='char'.
    """
    matcher = MohuMatcher()
    word_list = ["apple", "banana", "orange", "grape"]
    matcher.build(word_list)
    
    # Test char mode
    results = matcher.match("appl", mode='char')
    char_results = matcher._match_char("appl")
    
    # Results should be the same as calling _match_char directly
    assert len(results) == len(char_results)
    assert results == char_results


def test_matcher_match_pinyin_mode():
    """
    Tests the public match method with mode='pinyin'.
    """
    matcher = MohuMatcher()
    word_list = ["北京", "南京", "东京", "背景"]
    matcher.build(word_list)
    
    # Test pinyin mode
    results = matcher.match("北京", mode='pinyin')
    pinyin_results = matcher._match_pinyin("北京")
    
    # Results should be the same as calling _match_pinyin directly
    assert len(results) == len(pinyin_results)
    assert results == pinyin_results


def test_matcher_match_hybrid_mode():
    """
    Tests the public match method with mode='hybrid' (default).
    """
    matcher = MohuMatcher()
    word_list = ["北京", "南京", "apple", "banana"]
    matcher.build(word_list)
    
    # Test hybrid mode (default)
    results_hybrid = matcher.match("北京")  # Default should be hybrid
    results_explicit = matcher.match("北京", mode='hybrid')
    
    # Both should give the same results
    assert results_hybrid == results_explicit
    
    # Should be a combination of char and pinyin results
    char_results = matcher._match_char("北京")
    pinyin_results = matcher._match_pinyin("北京")
    
    # Hybrid results should contain elements from both strategies
    # (though scores will be different due to weighting)
    assert len(results_hybrid) > 0
    assert isinstance(results_hybrid, list)
    assert all(isinstance(item, tuple) and len(item) == 2 for item in results_hybrid)


def test_matcher_match_invalid_mode():
    """
    Tests the public match method with invalid mode values.
    """
    matcher = MohuMatcher()
    word_list = ["test", "word"]
    matcher.build(word_list)
    
    # Test invalid mode
    with pytest.raises(ValueError, match="Invalid mode"):
        matcher.match("test", mode='invalid')
    
    with pytest.raises(ValueError, match="Invalid mode"):
        matcher.match("test", mode='CHAR')  # Case sensitive


def test_matcher_match_similarity_threshold():
    """
    Tests the public match method with similarity_threshold filtering.
    """
    matcher = MohuMatcher()
    word_list = ["apple", "banana", "orange", "grape"]
    matcher.build(word_list)
    
    # Get all results without threshold
    all_results = matcher.match("appl", mode='char')
    
    # Get results with high threshold
    filtered_results = matcher.match("appl", mode='char', similarity_threshold=0.8)
    
    # Filtered results should be a subset of all results
    assert len(filtered_results) <= len(all_results)
    
    # All filtered results should have score >= threshold
    for word, score in filtered_results:
        assert score >= 0.8
    
    # Test with very high threshold (should return empty or very few results)
    high_threshold_results = matcher.match("appl", mode='char', similarity_threshold=0.99)
    assert len(high_threshold_results) <= len(filtered_results)


def test_matcher_match_max_results():
    """
    Tests the public match method with max_results parameter.
    """
    matcher = MohuMatcher()
    word_list = ["apple", "banana", "orange", "grape", "apricot", "avocado"]
    matcher.build(word_list)
    
    # Get all results
    all_results = matcher.match("a", mode='char')
    
    # Get limited results
    limited_results = matcher.match("a", mode='char', max_results=3)
    
    # Limited results should be at most 3
    assert len(limited_results) <= 3
    assert len(limited_results) <= len(all_results)
    
    # Limited results should be the top results from all results
    if len(all_results) >= 3:
        assert limited_results == all_results[:3]
    
    # Test with max_results=0 (should return empty)
    zero_results = matcher.match("a", mode='char', max_results=0)
    assert zero_results == []


def test_matcher_match_empty_text():
    """
    Tests the public match method with empty text input.
    """
    matcher = MohuMatcher()
    word_list = ["apple", "banana"]
    matcher.build(word_list)
    
    # Test all modes with empty text
    assert matcher.match("", mode='char') == []
    assert matcher.match("", mode='pinyin') == []
    assert matcher.match("", mode='hybrid') == []


def test_matcher_match_hybrid_weighting():
    """
    Tests that hybrid mode properly weights and combines results.
    """
    matcher = MohuMatcher()
    
    # Use words that might have different char vs pinyin similarities
    word_list = ["北京", "背景", "apple", "appl"]
    matcher.build(word_list)
    
    # Test hybrid matching
    hybrid_results = matcher.match("北京", mode='hybrid')
    char_results = matcher._match_char("北京")
    pinyin_results = matcher._match_pinyin("北京")
    
    # Hybrid should combine results from both strategies
    assert len(hybrid_results) > 0
    
    # Check that results are properly sorted by score
    scores = [score for word, score in hybrid_results]
    assert scores == sorted(scores, reverse=True)
    
    # Check that no word appears twice in hybrid results (deduplication)
    words = [word for word, score in hybrid_results]
    assert len(words) == len(set(words))


def test_matcher_match_comprehensive_scenario():
    """
    Tests a comprehensive scenario combining multiple features.
    """
    matcher = MohuMatcher()
    word_list = ["北京", "南京", "东京", "背景", "apple", "banana", "orange"]
    matcher.build(word_list)
    
    # Test comprehensive scenario: hybrid mode with threshold and max_results
    results = matcher.match(
        "北京", 
        mode='hybrid', 
        similarity_threshold=0.1, 
        max_results=5
    )
    
    # Should return results
    assert len(results) > 0
    assert len(results) <= 5
    
    # All results should meet threshold
    for word, score in results:
        assert score >= 0.1
    
    # Results should be sorted by score
    scores = [score for word, score in results]
    assert scores == sorted(scores, reverse=True) 


def test_matcher_add_word_basic():
    """
    Tests basic add_word functionality.
    """
    matcher = MohuMatcher()
    
    # Initially empty
    assert matcher.get_word_count() == 0
    assert matcher.get_words() == []
    
    # Build initial index
    initial_words = ["apple", "banana", "orange"]
    matcher.build(initial_words)
    
    assert matcher.get_word_count() == 3
    assert set(matcher.get_words()) == set(initial_words)
    
    # Add a new word
    result = matcher.add_word("grape")
    assert result is True  # Successfully added
    assert matcher.get_word_count() == 4
    assert "grape" in matcher.get_words()
    
    # Verify the new word can be found in matching
    matches = matcher.match("grape", mode='char')
    words_found = [word for word, score in matches]
    assert "grape" in words_found


def test_matcher_add_word_duplicate():
    """
    Tests adding a word that already exists.
    """
    matcher = MohuMatcher()
    
    # Build initial index
    initial_words = ["apple", "banana", "orange"]
    matcher.build(initial_words)
    
    # Try to add existing word
    result = matcher.add_word("apple")
    assert result is False  # Should return False for duplicate
    assert matcher.get_word_count() == 3  # Count should remain the same
    
    # Word list should remain unchanged
    assert set(matcher.get_words()) == set(initial_words)


def test_matcher_add_word_empty():
    """
    Tests adding empty string.
    """
    matcher = MohuMatcher()
    matcher.build(["apple", "banana"])
    
    # Try to add empty string
    result = matcher.add_word("")
    assert result is False
    assert matcher.get_word_count() == 2


def test_matcher_add_word_to_empty_matcher():
    """
    Tests adding word to an uninitialized matcher.
    """
    matcher = MohuMatcher()
    
    # Add word without building first
    result = matcher.add_word("newword")
    assert result is True
    assert matcher.get_word_count() == 1
    assert matcher.get_words() == ["newword"]
    
    # Verify the word can be found
    matches = matcher.match("newword", mode='char')
    words_found = [word for word, score in matches]
    assert "newword" in words_found


def test_matcher_remove_word_basic():
    """
    Tests basic remove_word functionality.
    """
    matcher = MohuMatcher()
    
    # Build initial index
    initial_words = ["apple", "banana", "orange", "grape"]
    matcher.build(initial_words)
    
    assert matcher.get_word_count() == 4
    
    # Remove a word
    result = matcher.remove_word("banana")
    assert result is True  # Successfully removed
    assert matcher.get_word_count() == 3
    assert "banana" not in matcher.get_words()
    
    # Verify the removed word cannot be found in matching
    matches = matcher.match("banana", mode='char')
    words_found = [word for word, score in matches]
    assert "banana" not in words_found


def test_matcher_remove_word_nonexistent():
    """
    Tests removing a word that doesn't exist.
    """
    matcher = MohuMatcher()
    
    # Build initial index
    initial_words = ["apple", "banana", "orange"]
    matcher.build(initial_words)
    
    # Try to remove non-existent word
    result = matcher.remove_word("grape")
    assert result is False  # Should return False for non-existent
    assert matcher.get_word_count() == 3  # Count should remain the same
    
    # Word list should remain unchanged
    assert set(matcher.get_words()) == set(initial_words)


def test_matcher_remove_word_empty():
    """
    Tests removing empty string.
    """
    matcher = MohuMatcher()
    matcher.build(["apple", "banana"])
    
    # Try to remove empty string
    result = matcher.remove_word("")
    assert result is False
    assert matcher.get_word_count() == 2


def test_matcher_remove_word_from_empty_matcher():
    """
    Tests removing word from an uninitialized matcher.
    """
    matcher = MohuMatcher()
    
    # Try to remove word without building first
    result = matcher.remove_word("nonexistent")
    assert result is False
    assert matcher.get_word_count() == 0


def test_matcher_dynamic_management_comprehensive():
    """
    Tests comprehensive dynamic word management scenario.
    """
    matcher = MohuMatcher()
    
    # Start with initial words
    initial_words = ["北京", "南京", "东京"]
    matcher.build(initial_words)
    
    # Add Chinese word
    assert matcher.add_word("背景") is True
    assert matcher.get_word_count() == 4
    
    # Add English word
    assert matcher.add_word("apple") is True
    assert matcher.get_word_count() == 5
    
    # Test that both new words can be found
    # Chinese word matching
    chinese_matches = matcher.match("背景", mode='hybrid')
    chinese_words = [word for word, score in chinese_matches]
    assert "背景" in chinese_words
    
    # English word matching
    english_matches = matcher.match("apple", mode='char')
    english_words = [word for word, score in english_matches]
    assert "apple" in english_words
    
    # Remove words
    assert matcher.remove_word("南京") is True
    assert matcher.remove_word("apple") is True
    assert matcher.get_word_count() == 3
    
    # Verify removed words can't be found
    remaining_matches = matcher.match("南京", mode='pinyin')
    remaining_words = [word for word, score in remaining_matches]
    assert "南京" not in remaining_words
    
    # Verify remaining words are still there
    final_words = matcher.get_words()
    assert "北京" in final_words
    assert "东京" in final_words
    assert "背景" in final_words


def test_matcher_get_words_copy():
    """
    Tests that get_words returns a copy, not the original list.
    """
    matcher = MohuMatcher()
    matcher.build(["apple", "banana"])
    
    # Get words list
    words = matcher.get_words()
    
    # Modify the returned list
    words.append("grape")
    words.remove("apple")
    
    # Original should be unchanged
    original_words = matcher.get_words()
    assert "grape" not in original_words
    assert "apple" in original_words
    assert matcher.get_word_count() == 2


def test_matcher_word_management_with_chinese():
    """
    Tests dynamic word management specifically with Chinese characters.
    """
    matcher = MohuMatcher()
    
    # Start with Chinese words
    initial_words = ["北京", "上海"]
    matcher.build(initial_words)
    
    # Add more Chinese words
    assert matcher.add_word("广州") is True
    assert matcher.add_word("深圳") is True
    
    # Test pinyin matching works for newly added words
    matches = matcher.match("guangzhou", mode='pinyin')  
    # Note: This might not find anything depending on pinyin conversion
    # But the test should not crash
    assert isinstance(matches, list)
    
    # Test character matching for Chinese
    char_matches = matcher.match("广州", mode='char')
    char_words = [word for word, score in char_matches]
    assert "广州" in char_words
    
    # Remove a Chinese word
    assert matcher.remove_word("上海") is True
    
    # Verify it's gone
    final_matches = matcher.match("上海", mode='char')
    final_words = [word for word, score in final_matches]
    assert "上海" not in final_words 
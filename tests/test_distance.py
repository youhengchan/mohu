"""
Tests for the weighted_levenshtein distance function.
"""
import pytest
from mohu.distance import weighted_levenshtein

# Test cases for weighted Levenshtein distance function
# Format: (seq1, seq2, confusion_matrix, expected_similarity)
TEST_CASES = [
    # --- Basic Cases (no weights) ---
    # Identical strings
    ("test", "test", None, 1.0),
    # Complete substitution
    ("cat", "dog", None, 0.0),
    # Single substitution
    ("book", "boot", None, 0.75),  # 1 substitution, len 4 -> sim = 1 - 1/4
    # Single deletion
    ("apple", "aple", None, 0.8),  # 1 deletion, len 5 -> sim = 1 - 1/5
    # Single insertion
    ("aple", "apple", None, 0.8),  # 1 insertion, len 5 -> sim = 1 - 1/5
    # Empty strings
    ("", "", None, 1.0),
    ("test", "", None, 0.0), # 4 deletions, len 4 -> sim = 1 - 4/4
    ("", "test", None, 0.0), # 4 insertions, len 4 -> sim = 1 - 4/4
    # sequences of different lengths
    ("intention", "execution", None, 1 - (5 / 9)), # Standard example, 5 edits

    # --- Weighted Cases ---
    # Weighted substitution (cheaper)
    ("text", "test", {"x": {"s": 0.4}}, 1 - (0.4 / 4)), # sim = 1 - 0.4/4 = 0.9
    # Weighted substitution (more expensive, but shouldn't exceed 1.0)
    ("text", "test", {"x": {"s": 1.5}}, 1 - (1.0 / 4)), # Capped at 1.0 standard substitution
    # No effect if the wrong characters are in the matrix
    ("text", "test", {"a": {"b": 0.1}}, 0.75), # Standard substitution cost
    # Mixed operations. Let's trace "caet" -> "fast"
    # c -> f (cost 0.5 from matrix)
    # a -> a (cost 0.0)
    # e -> s (cost 1.0, not in matrix)
    # t -> t (cost 0.0)
    # Total distance should be 1.5. Similarity = 1 - 1.5/4 = 0.625
    ("caet", "fast", {"c": {"f": 0.5}, "e": {"a": 0.2}}, 1 - (1.5 / 4)),


    # --- List-based cases (e.g., pinyin) ---
    # Identical lists
    (["bei", "jing"], ["bei", "jing"], None, 1.0),
    # Single substitution in list
    (["bei", "jing"], ["bei", "ping"], None, 0.5), # 1 sub, len 2 -> sim = 1 - 1/2
    # Weighted substitution in list
    (["zhong", "guo"], ["zong", "guo"], {"zhong": {"zong": 0.1}}, 1 - (0.1/2)), # 0.95
]

@pytest.mark.parametrize(
    "seq1, seq2, confusion_matrix, expected_similarity", TEST_CASES
)
def test_weighted_levenshtein(seq1, seq2, confusion_matrix, expected_similarity):
    """
    Tests the weighted_levenshtein function with various inputs.
    """
    result = weighted_levenshtein(seq1, seq2, confusion_matrix)
    assert result == pytest.approx(expected_similarity, abs=1e-9)

def test_return_value_range():
    """
    Test that the return value is always between 0.0 and 1.0.
    """
    # Highly dissimilar
    score1 = weighted_levenshtein("abcdefg", "hijklmn")
    assert 0.0 <= score1 <= 1.0

    # Highly similar
    score2 = weighted_levenshtein("abcdefg", "abcdefh")
    assert 0.0 <= score2 <= 1.0

    # With weights
    score3 = weighted_levenshtein("a", "b", {"a": {"b": 0.1}})
    assert 0.0 <= score3 <= 1.0
    
    # Negative score guard
    score4 = weighted_levenshtein("a", "b", {"a": {"b": 2.0}})
    assert 0.0 <= score4 <= 1.0 # distance is capped at 1.0, so sim is 1 - 1/1 = 0
    assert score4 == 0.0 
"""
This module provides a generic weighted Levenshtein distance calculator.
"""
from typing import Dict, Hashable, Optional, Sequence


def weighted_levenshtein(
    seq1: Sequence[Hashable],
    seq2: Sequence[Hashable],
    confusion_matrix: Optional[Dict[Hashable, Dict[Hashable, float]]] = None,
) -> float:
    """
    Calculates the weighted Levenshtein distance between two sequences and returns a similarity score.

    The similarity score is normalized to be between 0.0 and 1.0, where 1.0 means
    the sequences are identical. The cost of insertion and deletion is fixed at 1.0.
    The substitution cost is retrieved from the confusion matrix, defaulting to 1.0
    if the pair is not found.

    Args:
        seq1: The first sequence (e.g., a string or a list of pinyin syllables).
        seq2: The second sequence.
        confusion_matrix: A dictionary defining the substitution costs.
                          For example, `{'a': {'b': 0.5}}` means the cost of
                          substituting 'a' with 'b' is 0.5. Defaults to None.

    Returns:
        A float representing the similarity score between the two sequences.
    """
    if confusion_matrix is None:
        confusion_matrix = {}

    len1, len2 = len(seq1), len(seq2)
    max_len = max(len1, len2)

    if max_len == 0:
        return 1.0  # Both sequences are empty, so they are identical.

    # Initialize DP table. dp[i][j] will be the Levenshtein distance between
    # the first i characters of seq1 and the first j characters of seq2.
    dp = [[0.0] * (len2 + 1) for _ in range(len1 + 1)]

    # Initialize the first row and column of the DP table.
    # The distance of any first string to an empty second string is the
    # number of deletions to match them.
    for i in range(len1 + 1):
        dp[i][0] = float(i)
    for j in range(len2 + 1):
        dp[0][j] = float(j)

    # Fill DP table using the recurrence relation.
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            item1 = seq1[i - 1]
            item2 = seq2[j - 1]

            # Cost of insertion and deletion is always 1.0.
            deletion_cost = 1.0
            insertion_cost = 1.0

            # Get substitution cost.
            if item1 == item2:
                substitution_cost = 0.0
            else:
                # Default cost is 1.0, check confusion matrix for a specific cost.
                substitution_cost = confusion_matrix.get(item1, {}).get(item2, 1.0)
                # The substitution cost should not be greater than a standard substitution.
                substitution_cost = min(substitution_cost, 1.0)

            dp[i][j] = min(
                dp[i - 1][j] + deletion_cost,         # Deletion of item1
                dp[i][j - 1] + insertion_cost,        # Insertion of item2
                dp[i - 1][j - 1] + substitution_cost, # Substitution
            )

    # The final distance is in the bottom-right cell.
    distance = dp[len1][len2]

    # Normalize the distance to a similarity score.
    similarity = 1.0 - (distance / max_len)

    # Ensure the score is not below zero.
    return max(0.0, similarity) 
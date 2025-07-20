"""
This module implements an Aho-Corasick automaton for multi-pattern string matching,
optimized for fuzzy searching.
"""
from typing import Dict, Generic, Hashable, List, Optional, Set, TypeVar

T = TypeVar("T", bound=Hashable)


class ACAutomaton(Generic[T]):
    """
    An Aho-Corasick automaton for efficient multi-pattern matching with fuzzy search capabilities.

    The automaton is built from a dictionary of words. It supports adding words
    and then searching for them within a query sequence, allowing for a specified
    maximum Levenshtein distance.

    Attributes:
        _root: The root node of the Trie.
    """

    class Node:
        """
        A node in the Aho-Corasick Trie.

        Attributes:
            children: A dictionary mapping sequence items to child nodes.
            output: A set of complete words that end at this node.
            fail: The failure link to another node.
        """
        def __init__(self):
            self.children: Dict[T, ACAutomaton.Node] = {}
            self.output: Set[str] = set()
            self.fail: Optional[ACAutomaton.Node] = None

        def __repr__(self) -> str:
            return f"<Node children={list(self.children.keys())} output={self.output}>"

    def __init__(self):
        """Initializes the ACAutomaton with an empty root node."""
        self._root = self.Node()

    def add_word(self, word: str, sequence: List[T]):
        """
        Adds a word and its corresponding sequence to the Trie.

        This method builds the 'goto' function of the automaton.

        Args:
            word: The original word (string) to be stored as output.
            sequence: The sequence of items (e.g., characters or pinyin syllables)
                      representing the word.
        """
        if not sequence:
            return

        node = self._root
        for item in sequence:
            node = node.children.setdefault(item, self.Node())

        node.output.add(word)

    def make_automaton(self):
        """
        Finalizes the automaton by building the failure links.

        This method should be called after all words have been added.
        It uses a breadth-first search (BFS) to traverse the Trie and set
        the failure links for each node.
        """
        queue: List[ACAutomaton.Node] = []
        for node in self._root.children.values():
            node.fail = self._root
            queue.append(node)

        while queue:
            current_node = queue.pop(0)
            for item, next_node in current_node.children.items():
                queue.append(next_node)
                
                fail_node = current_node.fail
                while fail_node is not None and item not in fail_node.children:
                    fail_node = fail_node.fail

                if fail_node is not None:
                    next_node.fail = fail_node.children[item]
                    # Merging outputs is for standard AC search, not for our fuzzy search.
                    # If we need standard search later, we can create a separate method.
                    # if next_node.fail.output:
                    #     next_node.output.update(next_node.fail.output)
                else:
                    next_node.fail = self._root

    def search_fuzzy(self, query: List[T], max_distance: int) -> Set[str]:
        """
        Searches for all words in the automaton that are within a given
        Levenshtein distance of the query sequence.

        This search is based on the Trie structure and does not use the failure links.
        It's designed to find dictionary words that are "close" to a given query string.

        Args:
            query: The sequence of items to search for.
            max_distance: The maximum allowed Levenshtein distance.

        Returns:
            A set of matching words (candidates) found within the distance threshold.
        """
        results: Set[str] = set()
        
        if not query:
            return results
            
        # Initialize the first row of the DP table
        # dp[i] represents the cost of transforming an empty pattern to query[:i]
        current_row = list(range(len(query) + 1))
        
        # Start recursive search from root
        self._search_recursive_fixed(
            node=self._root,
            pattern_length=0,
            previous_row=current_row,
            query=query,
            max_distance=max_distance,
            results=results
        )
            
        return results

    def _search_recursive_fixed(
        self,
        node: "ACAutomaton.Node",
        pattern_length: int,
        previous_row: List[int],
        query: List[T],
        max_distance: int,
        results: Set[str],
    ):
        """
        A recursive helper that performs the fuzzy search with correct DP calculation.
        """
        # If this node represents a complete word, check if it's within distance
        if node.output and pattern_length > 0:  # Don't match empty pattern
            distance = previous_row[len(query)]
            if distance <= max_distance:
                results.update(node.output)

        # Pruning: if minimum distance in previous row exceeds threshold, stop
        if min(previous_row) > max_distance:
            return

        # Recursively search children
        for char, child_node in node.children.items():
            # Calculate new row of DP table
            current_row = [pattern_length + 1]  # Cost of deleting pattern chars
            
            for i in range(1, len(query) + 1):
                # Cost of deletion (remove char from query)
                delete_cost = previous_row[i] + 1
                
                # Cost of insertion (add char to query)  
                insert_cost = current_row[i - 1] + 1
                
                # Cost of substitution
                if query[i - 1] == char:
                    substitute_cost = previous_row[i - 1]  # No cost if match
                else:
                    substitute_cost = previous_row[i - 1] + 1
                
                current_row.append(min(delete_cost, insert_cost, substitute_cost))
            
            # Continue recursion with updated row
            self._search_recursive_fixed(
                node=child_node,
                pattern_length=pattern_length + 1,
                previous_row=current_row,
                query=query,
                max_distance=max_distance,
                results=results
            ) 
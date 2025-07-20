"""
This module contains the main MohuMatcher class, which is the primary interface
for the PyMOHU library.
"""
from typing import Dict, List, Optional, Set, Tuple

from .ac import ACAutomaton
from .config import (
    DEFAULT_CHAR_CONFUSION_PATH,
    DEFAULT_HYBRID_WEIGHTS,
    DEFAULT_IGNORE_TONES,
    DEFAULT_MAX_DISTANCE,
    DEFAULT_PINYIN_CONFUSION_PATH,
    DEFAULT_SIMILARITY_THRESHOLD,
)
from .distance import weighted_levenshtein
from .pinyin import PinyinConverter


class MohuMatcher:
    """
    The main class for fuzzy matching using pinyin and character-based strategies.
    
    This class orchestrates the pinyin conversion, AC automaton indexing, and distance
    calculation to find the best matches according to different matching modes.
    """

    def __init__(
        self,
        pinyin_confusion_path: str = DEFAULT_PINYIN_CONFUSION_PATH,
        char_confusion_path: str = DEFAULT_CHAR_CONFUSION_PATH,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
        max_distance: int = DEFAULT_MAX_DISTANCE,
        ignore_tones: bool = DEFAULT_IGNORE_TONES,
        hybrid_weights: Dict[str, float] = DEFAULT_HYBRID_WEIGHTS,
    ):
        """
        Initializes the MohuMatcher with user-defined or default configurations.

        Args:
            pinyin_confusion_path: Path to the pinyin confusion JSON file.
            char_confusion_path: Path to the character confusion JSON file.
            similarity_threshold: The minimum similarity score for a match.
            max_distance: The maximum Levenshtein distance for AC automaton search.
            ignore_tones: Whether to ignore tones in pinyin matching.
            hybrid_weights: Weights for combining scores in hybrid mode.
        """
        # Store configuration parameters
        self.pinyin_confusion_path = pinyin_confusion_path
        self.char_confusion_path = char_confusion_path
        self.similarity_threshold = similarity_threshold
        self.max_distance = max_distance
        self.ignore_tones = ignore_tones
        self.hybrid_weights = hybrid_weights.copy()  # Make a copy to avoid mutation

        # Initialize components
        self.pinyin_converter = PinyinConverter()

        # State variables - all initialized to None/empty
        self.char_ac_index: Optional[ACAutomaton[str]] = None
        self.pinyin_ac_index: Optional[ACAutomaton[str]] = None
        self.pinyin_map: Dict[str, Set[str]] = {}
        self.word_list: List[str] = []

        # Confusion matrices - will be loaded on demand
        self.pinyin_confusion: Optional[Dict] = None
        self.char_confusion: Optional[Dict] = None

    def build(self, word_list: List[str]) -> None:
        """
        Builds the internal indexes from a list of words.
        
        This method creates both character-based and pinyin-based AC automaton indexes
        to enable fuzzy matching in different modes.

        Args:
            word_list: A list of words to build the indexes from.
        """
        if not word_list:
            # Handle empty word list
            self.char_ac_index = None
            self.pinyin_ac_index = None
            self.pinyin_map = {}
            self.word_list = []
            return

        # Store the word list (remove duplicates while preserving order)
        seen = set()
        self.word_list = []
        for word in word_list:
            if word not in seen:
                self.word_list.append(word)
                seen.add(word)

        # Build character-based AC automaton index
        self.char_ac_index = ACAutomaton[str]()
        for word in word_list:
            # Convert word to character sequence
            char_sequence = list(word)
            self.char_ac_index.add_word(word, char_sequence)

        # Build pinyin-based index
        self.pinyin_ac_index = ACAutomaton[str]()
        self.pinyin_map = {}

        for word in word_list:
            # Convert word to pinyin sequence
            pinyin_sequence = self.pinyin_converter.convert(word, ignore_tones=self.ignore_tones)
            
            if pinyin_sequence:  # Only process if conversion was successful
                # Add to pinyin AC automaton
                self.pinyin_ac_index.add_word(word, pinyin_sequence)
                
                # Build pinyin map: pinyin_string -> set of original words
                pinyin_string = ''.join(pinyin_sequence)
                if pinyin_string not in self.pinyin_map:
                    self.pinyin_map[pinyin_string] = set()
                self.pinyin_map[pinyin_string].add(word)

    def _match_char(self, text: str) -> List[Tuple[str, float]]:
        """
        Performs character-based fuzzy matching.
        
        This method uses the character AC automaton to find candidate words
        and then scores them using weighted Levenshtein distance.

        Args:
            text: The input text to match against.

        Returns:
            A list of tuples (word, similarity_score) sorted by score descending.
        """
        if not text or self.char_ac_index is None:
            return []

        # Convert text to character sequence
        char_sequence = list(text)

        # Use AC automaton to find candidate words within max_distance
        candidates = self.char_ac_index.search_fuzzy(char_sequence, self.max_distance)

        if not candidates:
            return []

        # Load character confusion matrix if not already loaded
        if self.char_confusion is None:
            self.char_confusion = self._load_confusion_matrix(self.char_confusion_path)

        # Score each candidate using weighted Levenshtein distance
        scored_candidates = []
        for word in candidates:
            word_sequence = list(word)
            similarity = weighted_levenshtein(
                char_sequence, 
                word_sequence, 
                self.char_confusion
            )
            scored_candidates.append((word, similarity))

        # Sort by similarity score descending and return
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates

    def match(self, text: str, mode: str = 'hybrid', similarity_threshold: float = 0.0, max_results: int = None) -> List[Tuple[str, float]]:
        """
        Performs fuzzy matching on the input text using the specified mode.

        Args:
            text: The input text to match against.
            mode: The matching mode. Options:
                - 'char': Character-based matching only
                - 'pinyin': Pinyin-based matching only  
                - 'hybrid': Combination of character and pinyin matching (default)
            similarity_threshold: Minimum similarity score threshold (0.0-1.0).
                Results below this threshold will be filtered out.
            max_results: Maximum number of results to return. If None, returns all results.

        Returns:
            A list of tuples (word, similarity_score) sorted by score descending.

        Raises:
            ValueError: If mode is not one of 'char', 'pinyin', or 'hybrid'.
        """
        if not text:
            return []

        # Validate mode parameter
        valid_modes = {'char', 'pinyin', 'hybrid'}
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode '{mode}'. Must be one of {valid_modes}")

        # Get results based on mode
        if mode == 'char':
            results = self._match_char(text)
        elif mode == 'pinyin':
            results = self._match_pinyin(text)
        elif mode == 'hybrid':
            results = self._match_hybrid(text)
        else:
            # This should never happen due to validation above, but kept for safety
            raise ValueError(f"Unsupported mode: {mode}")

        # Apply similarity threshold filter
        if similarity_threshold > 0.0:
            results = [(word, score) for word, score in results if score >= similarity_threshold]

        # Apply max_results limit
        if max_results is not None and max_results > 0:
            results = results[:max_results]

        return results

    def _match_pinyin(self, text: str) -> List[Tuple[str, float]]:
        """
        Performs pinyin-based fuzzy matching.
        
        This method converts the input text to pinyin, uses the pinyin AC automaton
        to find candidate pinyin sequences, looks up the original words in pinyin_map,
        and scores them using weighted Levenshtein distance.

        Args:
            text: The input text to match against.

        Returns:
            A list of tuples (word, similarity_score) sorted by score descending.
        """
        if not text or self.pinyin_ac_index is None:
            return []

        # Convert text to pinyin sequence
        pinyin_sequence = self.pinyin_converter.convert(text, ignore_tones=self.ignore_tones)
        
        if not pinyin_sequence:
            return []

        # Use AC automaton to find candidate pinyin sequences within max_distance
        candidates = self.pinyin_ac_index.search_fuzzy(pinyin_sequence, self.max_distance)

        if not candidates:
            return []

        # Load pinyin confusion matrix if not already loaded
        if self.pinyin_confusion is None:
            self.pinyin_confusion = self._load_confusion_matrix(self.pinyin_confusion_path)

        # Collect original words from pinyin candidates and score them
        scored_candidates = []
        processed_words = set()  # Avoid duplicate scoring of the same word

        for candidate_word in candidates:
            # For each candidate word found by the AC automaton, 
            # get its pinyin and score it against our input pinyin
            candidate_pinyin = self.pinyin_converter.convert(candidate_word, ignore_tones=self.ignore_tones)
            
            if candidate_pinyin and candidate_word not in processed_words:
                similarity = weighted_levenshtein(
                    pinyin_sequence,
                    candidate_pinyin,
                    self.pinyin_confusion
                )
                scored_candidates.append((candidate_word, similarity))
                processed_words.add(candidate_word)

        # Sort by similarity score descending and return
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates

    def _match_hybrid(self, text: str) -> List[Tuple[str, float]]:
        """
        Performs hybrid matching combining character and pinyin-based approaches.
        
        This method calls both _match_char and _match_pinyin, then merges and 
        reweights the results to provide comprehensive fuzzy matching.

        Args:
            text: The input text to match against.

        Returns:
            A list of tuples (word, similarity_score) sorted by score descending.
        """
        # Get results from both matching strategies
        char_results = self._match_char(text)
        pinyin_results = self._match_pinyin(text)

        # Combine results using a dictionary to handle duplicates
        combined_scores = {}

        # Process character-based results with weight
        char_weight = 0.6  # Character matching gets 60% weight
        for word, score in char_results:
            combined_scores[word] = combined_scores.get(word, 0.0) + (score * char_weight)

        # Process pinyin-based results with weight  
        pinyin_weight = 0.4  # Pinyin matching gets 40% weight
        for word, score in pinyin_results:
            combined_scores[word] = combined_scores.get(word, 0.0) + (score * pinyin_weight)

        # Convert back to list and sort by combined score
        final_results = [(word, score) for word, score in combined_scores.items()]
        final_results.sort(key=lambda x: x[1], reverse=True)

        return final_results

    def add_word(self, word: str) -> bool:
        """
        Adds a new word to the matcher's dictionary and rebuilds indices.
        
        Args:
            word: The word to add to the dictionary.
            
        Returns:
            True if the word was added (wasn't already present), False if it was already in the dictionary.
        """
        if not word:
            return False
            
        # Check if word is already in the dictionary
        if hasattr(self, 'word_list') and word in self.word_list:
            return False
            
        # Initialize word_list if it doesn't exist
        if not hasattr(self, 'word_list') or self.word_list is None:
            self.word_list = []
            
        # Add the word to our word list
        self.word_list.append(word)
        
        # Rebuild the indices with the updated word list
        self.build(self.word_list)
        
        return True

    def remove_word(self, word: str) -> bool:
        """
        Removes a word from the matcher's dictionary and rebuilds indices.
        
        Args:
            word: The word to remove from the dictionary.
            
        Returns:
            True if the word was removed (was present), False if it wasn't in the dictionary.
        """
        if not word:
            return False
            
        # Check if word_list exists and contains the word
        if not hasattr(self, 'word_list') or self.word_list is None or word not in self.word_list:
            return False
            
        # Remove the word from our word list
        self.word_list.remove(word)
        
        # Rebuild the indices with the updated word list
        self.build(self.word_list)
        
        return True

    def get_word_count(self) -> int:
        """
        Returns the number of words currently in the dictionary.
        
        Returns:
            The count of words in the current dictionary.
        """
        if not hasattr(self, 'word_list') or self.word_list is None:
            return 0
        return len(self.word_list)

    def get_words(self) -> List[str]:
        """
        Returns a copy of the current word list.
        
        Returns:
            A list containing all words currently in the dictionary.
        """
        if not hasattr(self, 'word_list') or self.word_list is None:
            return []
        return self.word_list.copy()

    def _load_confusion_matrix(self, file_path: str) -> Dict:
        """
        Loads a confusion matrix from a JSON file.
        
        Args:
            file_path: Path to the JSON file containing the confusion matrix.
            
        Returns:
            The loaded confusion matrix as a dictionary, or empty dict if loading fails.
        """
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            # Return empty confusion matrix if loading fails
            # In a production system, you might want to log this error
            return {} 
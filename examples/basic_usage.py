#!/usr/bin/env python3
"""
PyMOHU Basic Usage Example

This example demonstrates how to use the PyMOHU library for fuzzy string matching
with both character-based and pinyin-based strategies.
"""

from mohu import MohuMatcher


def main():
    print("=" * 60)
    print("PyMOHU - Fuzzy String Matching Library Demo")
    print("=" * 60)
    
    # Create a MohuMatcher instance
    print("\n1. Creating MohuMatcher instance...")
    matcher = MohuMatcher()
    print(f"   Created matcher with max_distance={matcher.max_distance}")
    print(f"   Ignore tones: {matcher.ignore_tones}")
    
    # Build initial word dictionary
    print("\n2. Building word dictionary...")
    words = [
        # Chinese cities
        "北京", "南京", "东京", "西京", "背景",
        # English words
        "apple", "application", "apply", "april",
        "banana", "bandana", "band", "brand",
        # Mixed content
        "hello世界", "python编程", "AI人工智能"
    ]
    
    matcher.build(words)
    print(f"   Built dictionary with {matcher.get_word_count()} words")
    print(f"   Words: {', '.join(matcher.get_words()[:5])}...")
    
    # Demonstrate character-based matching
    print("\n3. Character-based matching examples...")
    demonstrate_char_matching(matcher)
    
    # Demonstrate pinyin-based matching
    print("\n4. Pinyin-based matching examples...")
    demonstrate_pinyin_matching(matcher)
    
    # Demonstrate hybrid matching (default)
    print("\n5. Hybrid matching examples...")
    demonstrate_hybrid_matching(matcher)
    
    # Demonstrate parameters and filtering
    print("\n6. Advanced parameters and filtering...")
    demonstrate_advanced_features(matcher)
    
    # Demonstrate dynamic word management
    print("\n7. Dynamic word management...")
    demonstrate_dynamic_management(matcher)
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


def demonstrate_char_matching(matcher):
    """Demonstrate character-based fuzzy matching."""
    test_queries = [
        ("appl", "apple"),      # Missing last character
        ("aple", "apple"),      # Missing middle character
        ("北", "北京"),          # Partial Chinese
        ("背", "背景"),          # Similar-looking Chinese characters
        ("banan", "banana"),    # Partial English word
    ]
    
    for query, description in test_queries:
        results = matcher.match(query, mode='char', max_results=3)
        print(f"   Query: '{query}' (looking for {description})")
        if results:
            for word, score in results:
                print(f"     - {word}: {score:.3f}")
        else:
            print("     - No matches found")
        print()


def demonstrate_pinyin_matching(matcher):
    """Demonstrate pinyin-based fuzzy matching."""
    test_queries = [
        ("beijing", "北京"),     # Romanized pinyin
        ("beij", "北京"),        # Partial pinyin
        ("nanjing", "南京"),     # Full romanized
        ("dongjing", "东京"),    # Another city
        ("背景", "背景"),         # Original Chinese
    ]
    
    for query, description in test_queries:
        results = matcher.match(query, mode='pinyin', max_results=3)
        print(f"   Query: '{query}' (looking for {description})")
        if results:
            for word, score in results:
                print(f"     - {word}: {score:.3f}")
        else:
            print("     - No matches found")
        print()


def demonstrate_hybrid_matching(matcher):
    """Demonstrate hybrid matching combining char and pinyin strategies."""
    test_queries = [
        "北京",        # Exact Chinese
        "bei",         # Partial pinyin
        "app",         # Partial English
        "python",      # English in mixed word
        "世界",        # Chinese in mixed word
    ]
    
    for query in test_queries:
        results = matcher.match(query, mode='hybrid', max_results=3)
        print(f"   Query: '{query}'")
        if results:
            for word, score in results:
                print(f"     - {word}: {score:.3f}")
        else:
            print("     - No matches found")
        print()


def demonstrate_advanced_features(matcher):
    """Demonstrate advanced parameters like threshold and max_results."""
    query = "app"
    
    # Different similarity thresholds
    print(f"   Query: '{query}' with different thresholds:")
    
    for threshold in [0.0, 0.5, 0.8]:
        results = matcher.match(query, mode='char', similarity_threshold=threshold)
        print(f"     Threshold {threshold}: {len(results)} results")
        for word, score in results[:2]:  # Show top 2
            print(f"       - {word}: {score:.3f}")
    
    print()
    
    # Different max_results limits
    print(f"   Query: '{query}' with different result limits:")
    for max_results in [1, 3, 10]:
        results = matcher.match(query, mode='char', max_results=max_results)
        print(f"     Max {max_results}: returned {len(results)} results")
    
    print()


def demonstrate_dynamic_management(matcher):
    """Demonstrate adding and removing words dynamically."""
    initial_count = matcher.get_word_count()
    print(f"   Initial word count: {initial_count}")
    
    # Add new words
    new_words = ["深圳", "广州", "orange", "grape"]
    print(f"   Adding words: {', '.join(new_words)}")
    
    for word in new_words:
        success = matcher.add_word(word)
        print(f"     Added '{word}': {success}")
    
    print(f"   New word count: {matcher.get_word_count()}")
    
    # Test matching with newly added words
    print("   Testing newly added words:")
    for word in ["深圳", "grape"]:
        results = matcher.match(word, max_results=1)
        if results:
            print(f"     Found '{word}': {results[0][1]:.3f}")
    
    # Remove some words
    words_to_remove = ["背景", "banana"]
    print(f"   Removing words: {', '.join(words_to_remove)}")
    
    for word in words_to_remove:
        success = matcher.remove_word(word)
        print(f"     Removed '{word}': {success}")
    
    print(f"   Final word count: {matcher.get_word_count()}")
    
    # Verify removed words are no longer found
    print("   Verifying removed words:")
    for word in words_to_remove:
        results = matcher.match(word, max_results=1)
        if results and results[0][0] == word:
            print(f"     ERROR: '{word}' still found!")
        else:
            print(f"     Confirmed: '{word}' removed")


if __name__ == "__main__":
    main() 
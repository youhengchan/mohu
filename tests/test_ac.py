"""
Tests for the Aho-Corasick automaton implementation.
"""
import pytest
from mohu.ac import ACAutomaton


@pytest.fixture
def basic_ac():
    """Provides a basic AC automaton with a few words for testing."""
    ac = ACAutomaton[str]()
    words_to_add = {
        "he": list("he"),
        "she": list("she"),
        "his": list("his"),
        "hers": list("hers"),
    }
    for word, sequence in words_to_add.items():
        ac.add_word(word, sequence)
    
    # In a real scenario, make_automaton() would be called here.
    # For now, we are only testing the Trie structure.
    return ac

def test_add_word_and_trie_structure(basic_ac):
    """
    Tests if the Trie (goto function) is built correctly.
    """
    # Root should have two children: 'h' and 's'
    assert len(basic_ac._root.children) == 2
    assert "h" in basic_ac._root.children
    assert "s" in basic_ac._root.children

    # Test path for "h"
    h_node = basic_ac._root.children["h"]
    assert len(h_node.children) == 2 # 'e' and 'i'
    assert "e" in h_node.children
    assert "i" in h_node.children
    assert not h_node.output # "h" is not a word

    # Test path for "he"
    he_node = h_node.children["e"]
    assert len(he_node.children) == 1 # 'r'
    assert "r" in he_node.children
    assert he_node.output == {"he"}

    # Test path for "hers"
    her_node = he_node.children["r"]
    assert "s" in her_node.children
    assert not her_node.output # "her" is not a word
    hers_node = her_node.children["s"]
    assert not hers_node.children # end of path
    assert hers_node.output == {"hers"}

    # Test path for "his"
    hi_node = h_node.children["i"]
    assert "s" in hi_node.children
    assert not hi_node.output # "hi" is not a word
    his_node = hi_node.children["s"]
    assert not his_node.children
    assert his_node.output == {"his"}

    # Test path for "s"
    s_node = basic_ac._root.children["s"]
    assert "h" in s_node.children
    assert not s_node.output

    # Test path for "she"
    sh_node = s_node.children["h"]
    assert "e" in sh_node.children
    assert not sh_node.output
    she_node = sh_node.children["e"]
    assert not she_node.children
    assert she_node.output == {"she"}

def test_add_empty_word():
    """Tests that adding an empty word does not affect the automaton."""
    ac = ACAutomaton[str]()
    ac.add_word("", [])
    assert len(ac._root.children) == 0
    assert not ac._root.output

def test_add_word_with_pinyin():
    """Tests adding a word represented by a list of pinyin syllables."""
    ac = ACAutomaton[str]()
    ac.add_word("北京", ["bei", "jing"])
    ac.add_word("背景", ["bei", "jing"]) # Add another word with same pinyin

    assert "bei" in ac._root.children
    bei_node = ac._root.children["bei"]
    assert "jing" in bei_node.children
    jing_node = bei_node.children["jing"]
    assert jing_node.output == {"北京", "背景"}


def test_make_automaton_failure_links(basic_ac):
    """
    Tests the failure link creation in the AC automaton.
    """
    # Finalize the automaton to build failure links
    basic_ac.make_automaton()
    root = basic_ac._root

    # Nodes at depth 1 should have their fail link point to the root
    h_node = root.children["h"]
    s_node = root.children["s"]
    assert h_node.fail == root
    assert s_node.fail == root

    # Test "she" path: s -> sh -> she
    sh_node = s_node.children["h"]
    she_node = sh_node.children["e"]
    # Fail link for "sh" should go to "h"
    assert sh_node.fail == h_node
    # Fail link for "she" should go to "he"
    he_node = h_node.children["e"]
    assert she_node.fail == he_node
    
    # Test "his" path: h -> hi -> his
    hi_node = h_node.children["i"]
    his_node = hi_node.children["s"]
    # Fail link for "hi" should go to root
    assert hi_node.fail == root
    # Fail link for "his" should go to "s"
    assert his_node.fail == s_node

    # Test "hers" path: h -> he -> her -> hers
    her_node = he_node.children["r"]
    hers_node = her_node.children["s"]
    # Fail link for "her" should go to root
    assert her_node.fail == root
    # Fail link for "hers" should go to "s"
    assert hers_node.fail == s_node

def test_failure_link_output_merging(basic_ac):
    """
    Tests that the output of a node is merged with the output of its fail link node.
    """
    basic_ac.make_automaton()
    
    # In the sequence "she", the node for "she" should have its output merged
    # with the output of its fail link, which is the node for "he".
    # So, the output for "she" should contain only "she".
    she_node = basic_ac._root.children["s"].children["h"].children["e"]
    assert she_node.output == {"she"}

    # The node for "he" should not be affected.
    he_node = basic_ac._root.children["h"].children["e"]
    assert he_node.output == {"he"}


@pytest.fixture
def pinyin_ac():
    """Provides an AC automaton with pinyin sequences."""
    ac = ACAutomaton[str]()
    ac.add_word("北京", ["bei", "jing"])
    ac.add_word("背景", ["bei", "jing"])
    # No make_automaton() call for fuzzy search testing
    return ac


@pytest.fixture
def fuzzy_ac():
    """Provides an AC automaton with a more diverse set of words for fuzzy testing."""
    ac = ACAutomaton[str]()
    words_to_add = {
        "apple": list("apple"),
        "apply": list("apply"),
        "banana": list("banana"),
        "bandana": list("bandana"),
        "orange": list("orange"),
        "cat": list("cat"),
    }
    for word, sequence in words_to_add.items():
        ac.add_word(word, sequence)
    # No make_automaton() call for fuzzy search testing
    return ac

def test_search_fuzzy_exact_match(fuzzy_ac):
    """Test search_fuzzy with max_distance=0 (exact matching)."""
    assert fuzzy_ac.search_fuzzy(list("apple"), 0) == {"apple"}
    assert fuzzy_ac.search_fuzzy(list("cat"), 0) == {"cat"}
    assert fuzzy_ac.search_fuzzy(list("appl"), 0) == set() # No exact match

def test_search_fuzzy_single_substitution(fuzzy_ac):
    """Test search_fuzzy with one substitution."""
    # "bapple" -> "apple" (1 substitution)
    assert fuzzy_ac.search_fuzzy(list("bapple"), 1) == {"apple"}
    # "bpply" -> "apply" (1 substitution)
    assert fuzzy_ac.search_fuzzy(list("bpply"), 1) == {"apply"}

def test_search_fuzzy_single_deletion(fuzzy_ac):
    """Test search_fuzzy with one deletion."""
    # "aple" -> "apple" (1 deletion from pattern)
    assert fuzzy_ac.search_fuzzy(list("aple"), 1) == {"apple"}
    # "bandna" -> "banana", "bandana"
    assert fuzzy_ac.search_fuzzy(list("bandna"), 1) == {"banana", "bandana"}
    
def test_search_fuzzy_single_insertion(fuzzy_ac):
    """Test search_fuzzy with one insertion."""
    # "appple" -> "apple" (1 insertion in pattern)
    assert fuzzy_ac.search_fuzzy(list("appple"), 1) == {"apple"}

def test_search_fuzzy_combined_and_larger_distance(fuzzy_ac):
    """Test search_fuzzy with combined edits and larger distance."""
    # "baple" -> "apple" (1 sub, 1 del) -> distance = 2
    assert fuzzy_ac.search_fuzzy(list("baple"), 1) == set()
    assert fuzzy_ac.search_fuzzy(list("baple"), 2) == {"apple"}
    
    # "banann" vs "banana" (1 deletion from query) -> distance = 1
    # "banann" vs "bandana" (1 insertion of 'd', 1 insertion of 'a') -> distance = 2  
    assert fuzzy_ac.search_fuzzy(list("banann"), 1) == {"banana"}
    assert fuzzy_ac.search_fuzzy(list("banann"), 2) == {"banana", "bandana"}
    
    # Test higher distance threshold
    assert fuzzy_ac.search_fuzzy(list("banann"), 3) == {"banana", "bandana"}


def test_search_fuzzy_no_match(fuzzy_ac):
    """Test search_fuzzy when no match is expected."""
    assert fuzzy_ac.search_fuzzy(list("xyz"), 1) == set()
    assert fuzzy_ac.search_fuzzy(list("application"), 2) == set()

def test_search_fuzzy_with_pinyin(pinyin_ac):
    """Test fuzzy search with Pinyin sequences."""
    # query: 'bei pign' -> should match 'bei jing' (1 substitution)
    assert pinyin_ac.search_fuzzy(["bei", "pign"], 1) == {"北京", "背景"}
    # query: 'bei' -> should match 'bei jing' (1 deletion)
    assert pinyin_ac.search_fuzzy(["bei"], 1) == {"北京", "背景"}
    # query: 'beng jing' -> should match 'bei jing' (1 substitution)
    assert pinyin_ac.search_fuzzy(["beng", "jing"], 1) == {"北京", "背景"}
    # No match
    assert pinyin_ac.search_fuzzy(["shang", "hai"], 0) == set() 
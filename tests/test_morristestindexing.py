from engine.indexing.postionalinvertedindex import PositionalInvertedIndex
import pytest


@pytest.fixture
def positional_index():
    index = PositionalInvertedIndex()
    index.addTerm("cat", 1, 0)
    index.addTerm("cat", 1, 2)
    index.addTerm("dog", 2, 1)
    return index


def test_get_postings_found(positional_index):
    postings = positional_index.getPostings("cat")
    assert len(postings) == 1
    assert postings[0].doc_id == 1
    assert postings[0].positions == [0, 2]


def test_get_postings_not_found(positional_index):
    postings = positional_index.getPostings("elephant")
    assert len(postings) == 0


def test_get_vocabulary(positional_index):
    vocab = positional_index.getVocabulary()
    assert len(vocab) == 2
    assert "cat" in vocab
    assert "dog" in vocab


def test_add_term_new(positional_index):
    positional_index.addTerm("fish", 3, 0)
    postings = positional_index.getPostings("fish")
    assert len(postings) == 1
    assert postings[0].doc_id == 3
    assert postings[0].positions == [0]


def test_add_term_existing(positional_index):
    positional_index.addTerm("cat", 3, 1)
    postings = positional_index.getPostings("cat")
    assert len(postings) == 2
    assert postings[1].doc_id == 3
    assert postings[1].positions == [1]


def test_add_term_same_doc(positional_index):
    positional_index.addTerm("cat", 1, 3)
    postings = positional_index.getPostings("cat")
    assert len(postings) == 1
    assert postings[0].doc_id == 1
    assert postings[0].positions == [0, 2, 3]

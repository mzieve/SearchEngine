from typing import Iterable
from .postings import Posting
from .index import Index

class PositionalInvertedIndex(Index):
    """Implements a positional inverted index."""

    def __init__(self):
        """Constructs an empty index"""
        self.index = dict()

    def getPostings(self, term: str) -> Iterable[Posting]:
        """Returns a list of Postings for all documents that contain the given term."""
        postings = []
        if term in self.index:
            postings = self.index[term]

        return postings

    def getVocabulary(self) -> Iterable[str]:
        vocab = sorted(self.index.keys())
        return vocab

    def addTerm(self, term: str, doc_id: int, position : int):
        """Records that the given document ID contains the given term at its current position."""
        if term not in self.index:
           self.index[term] = [Posting(doc_id, position)]
        else:
            latest_posting = self.index[term][-1]
            if latest_posting.doc_id < doc_id:
                self.index[term].append(Posting(doc_id, position))
            elif latest_posting.doc_id == doc_id:
                self.index[term][-1].positions.append(position)
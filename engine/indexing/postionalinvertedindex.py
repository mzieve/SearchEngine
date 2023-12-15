from typing import Iterable
from .postings import Posting
from .index import Index
import bisect


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

    def getVocabulary(self) -> list[str]:
        """Return the vocabulary of the poistional inverted index"""
        return sorted(self.index.keys())

    def addTerm(self, term: str, doc_id: int, position: int):
        """Records that the given document ID contains the given term at its current position."""
        if term:
            if term not in self.index:
                self.index[term] = [Posting(doc_id, [position])]
            else:
                postings_list = self.index[term]
                if postings_list[-1].doc_id == doc_id:
                    positions = postings_list[-1].positions
                    if positions[-1] < position:
                        positions.append(position)
                    else:
                        index = bisect.bisect_left(positions, position)
                        positions.insert(index, position)
                else:
                    postings_list.append(Posting(doc_id, [position]))

    def clear(self):
        """Clears the index."""
        self.index.clear()

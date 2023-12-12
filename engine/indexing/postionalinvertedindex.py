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

    def export_sorted_index(self) -> str:
        """
        Exports the index in a sorted and formatted manner suitable for writing to a file.
        """
        sorted_vocabulary = self.getVocabulary()
        formatted_index = ""

        for term in sorted_vocabulary:
            postings = self.getPostings(term)
            formatted_postings = self.format_postings(term, postings)
            formatted_index += formatted_postings + "\n"

        return formatted_index

    def format_postings(self, term: str, postings: Iterable[Posting]) -> str:
        """
        Formats the postings list of a term for export.
        Checks if positions are in ascending order for each term and document ID.
        """
        postings_str = ""
        for posting in postings:
            postings_str += f"{posting.doc_id},{','.join(map(str, posting.positions))};"

        return f"{term}: {postings_str[:-1]}"

    def clear(self):
        """Clears the index."""
        self.index.clear()

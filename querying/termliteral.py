from ..indexing.postings import Posting
from .querycomponent import QueryComponent

class TermLiteral(QueryComponent):
    """
    A TermLiteral represents a single term in a subquery.
    """

    def __init__(self, term : str):
        self.term = term

    def get_postings(self, index) -> list[Posting]:
        return index.get_postings(self.term)

    def __str__(self) -> str:
        return self.term
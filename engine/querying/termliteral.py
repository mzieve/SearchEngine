from engine.indexing import Posting
from .querycomponent import QueryComponent


class TermLiteral(QueryComponent):
    """
    A TermLiteral represents a single term in a subquery.
    """

    def __init__(self, term: str):
        self.term = term

    def getPostings(self, index, need_pos = False) -> list[Posting]:
        return index.getPostings(self.term, need_pos)

    def __str__(self) -> str:
        return self.term

    def matches(self, tokens: set) -> bool:
        return self.term in tokens

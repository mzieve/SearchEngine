from abc import ABC, abstractmethod
from engine.indexing import Posting


class QueryComponent(ABC):
    """
    A QueryComponent is one piece of a larger query, whether that piece is a literal string or represents a merging of
    other components. All nodes in a query parse tree are QueryComponent objects.
    """

    @abstractmethod
    def getPostings(self, index, need_pos) -> list[Posting]:
        """
        Retrieves a list of postings for the query component, using an Index as the source.
        """
        pass

    def is_positive(self) -> bool:
        """
        Returns true for all QueryComponents except for NotQuery components.
        :return:
        """
        return True

    @abstractmethod
    def matches(self, tokens: set) -> bool:
        pass

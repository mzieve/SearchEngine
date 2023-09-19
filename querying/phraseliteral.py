from indexing.postings import Posting
from .querycomponent import QueryComponent

class PhraseLiteral(QueryComponent):
    """
    Represents a phrase literal consisting of one or more terms that must occur in sequence.
    """

    def __init__(self, terms : list[QueryComponent]):
        self.literals = terms

    def get_postings(self, index) -> list[Posting]:
        return None
        # TODO: program this method. Retrieve the postings for the individual literals in the phrase,
		# and positional merge them together.

    def __str__(self) -> str:
        return '"' + " ".join(map(str, self.literals)) + '"'
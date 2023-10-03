from indexing.postings import Posting
from .querycomponent import QueryComponent

class PhraseLiteral(QueryComponent):
    """
    Represents a phrase literal consisting of one or more terms that must occur in sequence.
    """

    def __init__(self, terms : list[QueryComponent]):
        self.literals = terms

    def getPostings(self, index) -> list[Posting]:
        if not self.literals or isinstance(self.literals[0], TermLiteral):
            return []
            
        postings_lists = [literal.getPostings(index) for literal in self.literals if isinstance(literal, QueryComponent)]
        
        if not postings_lists or not all(postings_lists):
            return []
        
        result = []
        for postings in zip(*postings_lists):
            doc_id = postings[0].doc_id
            if all(posting.doc_id == doc_id for posting in postings):
                positions_list = [posting.positions for posting in postings]
                for positions in zip(*positions_list):
                    if all(position == positions[0] + i for i, position in enumerate(positions)):
                        result.append(Posting(doc_id, positions))
        return result

    def __str__(self) -> str:
        return '"' + " ".join(map(str, self.literals)) + '"'
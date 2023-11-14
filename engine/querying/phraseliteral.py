from engine.indexing import Posting
from .querycomponent import QueryComponent
from .termliteral import TermLiteral


class PhraseLiteral(QueryComponent):
    """
    Represents a phrase literal consisting of one or more terms that must occur in sequence.
    """

    def __init__(self, terms: list[QueryComponent]):
        self.literals = terms

    def getPostings(self, index) -> list[Posting]:
        if not self.literals or not isinstance(self.literals[0], TermLiteral):
            return []

        postings_lists = [
            literal.getPostings(index, True)
            for literal in self.literals
            if isinstance(literal, QueryComponent)
        ]

        if not postings_lists or not all(postings_lists):
            return []

        result_postings = postings_lists[0]

        for next_postings in postings_lists[1:]:
            result_postings = PhraseLiteral.positional_intersect(
                result_postings, next_postings
            )

        return result_postings

    @staticmethod
    def positional_intersect(p1: list[Posting], p2: list[Posting]) -> list[Posting]:
        answer = []
        i, j = 0, 0

        while i < len(p1) and j < len(p2):
            if p1[i].doc_id == p2[j].doc_id:
                positions = []
                for pos in p1[i].positions:
                    if pos + 1 in p2[j].positions:
                        positions.append(pos + 1)

                if positions:
                    posting = Posting(p1[i].doc_id, positions[0])
                    posting.positions.extend(positions[1:])
                    answer.append(posting)

                i += 1
                j += 1
            elif p1[i].doc_id < p2[j].doc_id:
                i += 1
            else:
                j += 1

        return answer

    def __str__(self) -> str:
        return '"' + " ".join(map(str, self.literals)) + '"'

    def matches(self, tokens: set) -> bool:
        return all(literal.matches(tokens) for literal in self.literals)

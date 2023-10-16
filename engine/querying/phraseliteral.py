from engine.indexing import Posting
from .querycomponent import QueryComponent
from .termliteral import TermLiteral

class PhraseLiteral(QueryComponent):
    """
    Represents a phrase literal consisting of one or more terms that must occur in sequence.
    """

    def __init__(self, terms : list[QueryComponent]):
        self.literals = terms

    def getPostings(self, index) -> list[Posting]:
        if not self.literals or not isinstance(self.literals[0], TermLiteral):
            return []

        postings_lists = [literal.getPostings(index) for literal in self.literals if isinstance(literal, QueryComponent)]

        if not postings_lists or not all(postings_lists):
            return []

        for literal, postings in zip(self.literals, postings_lists):
            print(f"'{literal}': {postings}")

        result_postings = postings_lists[0]
        k = len(self.literals) - 1
        for next_postings in postings_lists[1:]:
            result_postings = PhraseLiteral.positional_intersect(result_postings, next_postings, k)

        return result_postings

    @staticmethod
    def positional_intersect(p1: list[Posting], p2: list[Posting], k: int) -> list[Posting]:
        """ Proximity Intersection Algorithm"""
        answer = []
        i, j = 0, 0
        
        while i < len(p1) and j < len(p2):
            if p1[i].doc_id == p2[j].doc_id:
                l = []
                positions_p1 = p1[i].positions[:]
                positions_p2 = p2[j].positions[:]
                pp1, pp2 = 0, 0
                
                while pp1 < len(positions_p1):
                    while pp2 < len(positions_p2):
                        if abs(positions_p1[pp1] - positions_p2[pp2]) <= k:
                            l.append(positions_p2[pp2])
                        elif positions_p2[pp2] > positions_p1[pp1]:
                            break
                        pp2 += 1

                    l = [pos for pos in l if abs(pos - positions_p1[pp1]) <= k]
                    
                    for pos in l:
                        answer.append(Posting(p1[i].doc_id, positions_p1[pp1]))
                        answer[-1].positions = [pos]
                        
                    pp1 += 1
                    
                i += 1
                j += 1
            elif p1[i].doc_id < p2[j].doc_id:
                i += 1
            else:
                j += 1
        
        return answer

    def __str__(self) -> str:
        return '"' + " ".join(map(str, self.literals)) + '"'
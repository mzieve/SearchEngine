from .querycomponent import QueryComponent
from ..indexing import Index, Posting

from . import querycomponent

class AndQuery(QueryComponent):
    def __init__(self, components : list[QueryComponent]):
        # please don't rename the "components" field.
        self.components = components

    def get_postings(self, index : Index) -> list[Posting]:
        #result = []
        # TODO: program the merge for an AndQuery, by gathering the postings of the composed QueryComponents and
		# intersecting the resulting postings.
        result = self.components[0].get_postings()
        for component in self.components[1:]:
            '''AND the component postings with the result. For two different words, we would AND their postings'
             doc ID's, but I am not sure what to do with their different positions. Discuss this w Morris. '''
            new_postings = component.get_postings()
            result = self._and_op(result, new_postings)
        return result

    def _and_op(self, first_postings, second_postings):
        result = []
        i, j = 0, 0
        first_p_len, second_p_len = len(first_postings), len(second_postings)
        while (i < first_p_len) and (j < second_p_len):
            first_p_doc_id = first_postings[i].doc_id
            second_p_doc_id = second_postings[j].doc_id
            if first_p_doc_id == second_p_doc_id:
                result.append(first_p_doc_id)
            elif first_p_doc_id < second_p_doc_id:
                i += 1
            else:
                j += 1
        return result

    def __str__(self):
        return " AND ".join(map(str, self.components))
from .querycomponent import QueryComponent
from engine.indexing import Index, Posting
from .notquery import NotQuery

class AndQuery(QueryComponent):
    def __init__(self, components : list[QueryComponent]):
        # please don't rename the "components" field.
        self.components = components

    def getPostings(self, index : Index) -> list[Posting]:
        #result = []
        # TODO: program the merge for an AndQuery, by gathering the postings of the composed QueryComponents and
		# intersecting the resulting postings.
        result = self.components[0].getPostings(index)
        for component in self.components[1:]:
            not_component = True if component.is_positive() == False else False
            new_postings = component.getPostings(index)
            result = self._and_op(result, new_postings, not_component)
        return result

    def _and_op(self, first_postings, second_postings, not_component):
        result = []
        i, j = 0, 0
        first_p_len, second_p_len = len(first_postings), len(second_postings)
        while (i < first_p_len) and (j < second_p_len):
            first_p_doc_id = first_postings[i].doc_id
            second_p_doc_id = second_postings[j].doc_id
            if first_p_doc_id == second_p_doc_id:
                if not not_component:
                    result.append(first_postings[i])
                i += 1
                j += 1
            elif first_p_doc_id < second_p_doc_id:
                if not_component:
                    result.append(first_postings[i])
                i += 1
            else:
                j += 1
        return result

    def __str__(self):
        return " AND ".join(map(str, self.components))

    def matches(self, tokens: set) -> bool:
        return all(component.matches(tokens) for component in self.components)

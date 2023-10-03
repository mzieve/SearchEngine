from .querycomponent import QueryComponent
from indexing import Index, Posting

from querying import querycomponent 

class AndQuery(QueryComponent):
    def __init__(self, components : list[QueryComponent]):
        # please don't rename the "components" field.
        self.components = components

    def get_postings(self, index: Index) -> list[Posting]:
        if not self.components:
            return []

        # Get postings list for the first component
        result_postings = self.components[0].get_postings(index)
        for component in self.components[1:]:
            other_postings = component.get_postings(index)

            # Find common document ids
            result_doc_ids = {posting.doc_id for posting in result_postings}
            other_doc_ids = {posting.doc_id for posting in other_postings}

            # Intersect the postings based on document ids
            common_doc_ids = result_doc_ids.intersection(other_doc_ids)
            result_postings = [posting for posting in result_postings if posting.doc_id in common_doc_ids]

        return result_postings
        
    def __str__(self):
        return " AND ".join(map(str, self.components))
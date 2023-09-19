from .querycomponent import QueryComponent
from indexing import Index, Posting

from querying import querycomponent 

class OrQuery(QueryComponent):
    def __init__(self, components : list[QueryComponent]):
        self.components = components

    def get_postings(self, index : Index) -> list[Posting]:
        result = []
        # TODO: program the merge for an OrQuery, by gathering the postings of the composed QueryComponents and
		# merging the resulting postings.
        return result

    def __str__(self):
        return "(" + " OR ".join(map(str, self.components)) + ")"
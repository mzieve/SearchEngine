from .querycomponent import QueryComponent
from indexing import Index, Posting

from querying import querycomponent 

class OrQuery(QueryComponent):
    def __init__(self, components : list[QueryComponent]):
        self.components = components

    def get_postings(self, index : Index) -> list[Posting]:
        result = set()
        for component in self.components:
            result.update(component.get_postings(index))
        return list(result)

    def __str__(self):
        return "(" + " OR ".join(map(str, self.components)) + ")"
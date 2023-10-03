from .querycomponent import QueryComponent
from engine.indexing import Index, Posting
from . import querycomponent

class OrQuery(QueryComponent):
    def __init__(self, components : list[QueryComponent]):
        self.components = components

    def getPostings(self, index : Index) -> list[Posting]:
        result = set()
        for component in self.components:
            result.update(component.getPostings(index))
        return list(result)

    def __str__(self):
        return "(" + " OR ".join(map(str, self.components)) + ")"
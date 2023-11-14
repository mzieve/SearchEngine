from .querycomponent import QueryComponent
from ..indexing import Index, Posting


class NotQuery(QueryComponent):
    def __init__(self, component: QueryComponent):
        self.component = component

    def is_positive(self) -> bool:
        return False

    def getPostings(self, index) -> list[Posting]:
        return self.component.getPostings(index, False)

    def __str__(self):
        return f"NOT ({str(self.component)})"

    def matches(self, tokens: set) -> bool:
        return not self.component.matches(tokens)

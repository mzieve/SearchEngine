from .querycomponent import QueryComponent
from engine.indexing import Index, Posting
from . import querycomponent

class OrQuery(QueryComponent):
    def __init__(self, components : list[QueryComponent]):
        self.components = components

    def getPostings(self, index : Index) -> list[Posting]:
        document_ids = set()
        postings = []
        
        for component in self.components:
            for posting in component.getPostings(index):
                if posting.doc_id not in document_ids:  
                    postings.append(posting)
                    document_ids.add(posting.doc_id) 
                    
        return postings

    def __str__(self):
        return "(" + " OR ".join(map(str, self.components)) + ")"

    def matches(self, tokens: set) -> bool:
        return any(component.matches(tokens) for component in self.components)

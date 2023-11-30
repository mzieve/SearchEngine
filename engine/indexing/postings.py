class Posting:
    """A Posting encapulates a document ID associated with a search query component."""

    def __init__(self, doc_id: int, positions=None):
        self.doc_id = doc_id
        if positions is None:
            self.positions = []
        elif isinstance(positions, int):
            self.positions = [positions] 
        else:
            self.positions = positions

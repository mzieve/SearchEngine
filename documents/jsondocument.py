from pathlib import Path
from typing import Iterable
from .document import Document

class JsonDocument(Document):
    def __init__(self, id: int, title: str, content: str):
        """Initialize a JsonDocument instance."""
        super().__init__(id)
        self._title = title
        self._content = content

    @property
    def title(self) -> str:
        """Return the title of the document."""
        return self._title

    def get_content(self) -> Iterable[str]:
        """Yield the content of the document as an iterable."""
        yield self._content

    @staticmethod
    def load_from(doc_id: int, title: str, content: str) -> 'JsonDocument':
        """Static method to load a JsonDocument."""
        return JsonDocument(doc_id, title, content)
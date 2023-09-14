from pathlib import Path
from typing import Iterable
from .document import Document

class TextFileDocument(Document):
    def __init__(self, id: int, title: str, content: str):
        """Initialize a TextFileDocument instance."""
        super().__init__(id)
        self._title = title
        self._content = content

    @property
    def title(self) -> str:
        """Return the title of the document."""
        return self._title

    def get_content(self) -> Iterable[str]:
        """Yield the content of the document as an iterable."""
        yield self._content  # Changed from open(self.path)

    @staticmethod
    def load_from(doc_id: int, title: str, content: str) -> 'TextFileDocument':
        """Static method to load a TextFileDocument."""
        return TextFileDocument(doc_id, title, content)
	
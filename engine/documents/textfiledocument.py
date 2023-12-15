from pathlib import Path
from typing import Iterable
from .document import Document


class TextFileDocument(Document):
    def __init__(self, id: int, path: Path):
        """Initialize a TextFileDocument instance."""
        super().__init__(id)
        self.path = path

    @property
    def title(self) -> str:
        """Return the title of the document."""
        return self.path.stem

    def get_content(self) -> Iterable[str]:
        """Yield the content of the document as an iterable."""
        with open(self.path, 'r', encoding='utf-8') as file:
            yield from file

    @staticmethod
    def load_from(abs_path: Path, doc_id: int) -> "TextFileDocument":
        """Static method to load a TextFileDocument."""
        return TextFileDocument(doc_id, abs_path)

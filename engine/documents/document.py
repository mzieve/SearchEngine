from abc import ABC, abstractmethod, abstractproperty
from typing import Iterable


class Document(ABC):
    """Initialize the Document components."""

    def __init__(self, docID: int):
        self.id = docID

    @abstractmethod
    def get_content(self) -> Iterable[str]:
        """Return the document content as an iterable of strings."""
        pass

    @abstractproperty
    def title(self) -> str:
        """Return the title of the document. Not implemented here."""
        pass

    def __str__(self) -> str:
        """Return the string representation of the Document."""
        return f"{self.title} (ID {self.id})"

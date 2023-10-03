from abc import ABC, abstractmethod
from typing import Iterable

class Document(ABC):
	"""Initialize the Document components."""
	def __init__(self, docID : int):
	    self.id = docID  # Initialize the document ID

	"""Return the document content as an iterable of strings."""
	@abstractmethod
	def get_content(self) -> Iterable[str]:
	    pass

	"""Return the title of the document. Not implemented here."""
	def title(self) -> str:
	    pass

	"""Return the string representation of the Document."""
	def __str__(self) -> str:
	    return f"{self.title} (ID {self.id})"

	
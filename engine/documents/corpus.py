from abc import ABC, abstractmethod
from typing import Iterable, Iterator
from .document import Document

class DocumentCorpus(ABC):
	"""Return an iterable of all documents in the corpus."""
	@abstractmethod
	def documents(self) -> Iterable[Document]:
		pass

	"""Return the number of documents in the corpus."""
	@abstractmethod
	def __len__(self) -> int:
		pass

	"""Return a specific document by its ID."""
	@abstractmethod
	def get_document(self, doc_id) -> Document:
		pass

	"""Make the corpus iterable. Delegates to self.documents()."""
	def __iter__(self) -> Iterator[Document]:
		return iter(self.documents())
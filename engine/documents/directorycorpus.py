from typing import Callable, Iterable, Iterator, Optional
from collections import defaultdict
from .document import Document
from pathlib import Path
from . import textfiledocument, jsondocument, xmldocument
from typing import Dict, Optional
from config import TOTAL_DOCS
import json


class DirectoryCorpus:
    """
    Initialize a DirectoryCorpus instance.

    Args:
        abs_path: Absolute path to the directory containing documents.
        fileFilter: Callable to filter files. By default, accepts all.
        factories: Dictionary mapping file extensions to factory methods for Document instances.
    """

    def __init__(
        self,
        abs_path: Path,
        file_filter: Callable[[Path], bool] = lambda p: True,
        factories: Optional[Dict[str, Callable[..., Document]]] = None,
    ):
        self.corpus_path = abs_path
        self.file_filter = file_filter

        default_factories: Dict[str, Callable[..., Document]] = {
            ".txt": textfiledocument.TextFileDocument.load_from,
            ".json": jsondocument.JsonDocument.load_from,
            ".xml": xmldocument.XMLDocument.load_from,
        }

        def unsupported_file_type(*args, **kwargs) -> Document:
            raise ValueError("Unsupported file type")

        self.factories: Dict[str, Callable[..., Document]] = factories or defaultdict(
            lambda: unsupported_file_type
        )
        self.factories.update(default_factories)
        self._documents: Dict[int, Document] = {}

    def documents(self) -> Iterable[Document]:
        """Return an iterable over all Document instances in the corpus."""
        return self._documents.values()

    def __iter__(self) -> Iterator[Document]:
        """Make the DirectoryCorpus class iterable over its Document instances."""
        return iter(self.documents())

    def __len__(self) -> int:
        """Return the total number of documents in the corpus."""
        return len(self._documents)

    def __getitem__(self, index):
        return list(self.documents())[index]

    def get_document(self, docID: int) -> Optional[Document]:
        """Return a Document instance by its ID."""
        return self._documents.get(docID, None)

    def load_documents_generator(self) -> Iterable[Document]:
        """Generator method to yield documents one by one from the directory."""
        next_id = 0
        for f in Path(self.corpus_path).rglob("*"):
            if f.suffix in self.factories and self.file_filter(f):
                if f.suffix == ".json":
                    with open(f, "r", encoding="utf-8") as json_file:
                        data = json.load(json_file)
                    title = data.get("title", "")
                    content = data.get("body", "")
                    yield self.factories[f.suffix](next_id, title, content)
                else:
                    yield self.factories[f.suffix](f, next_id)
                next_id += 1
        global TOTAL_DOCS
        TOTAL_DOCS = next_id

    @staticmethod
    def load_directory(
        path: Path, extensionFactories: Dict[str, Callable[[Path, int], Document]]
    ) -> "DirectoryCorpus":
        """
        Static method to load a directory and return a DirectoryCorpus instance.

        Args:
            path: The directory path.
            extensionFactories: Dictionary mapping file extensions to factory methods.
        """
        return DirectoryCorpus(
            path,
            lambda f: f.suffix in extensionFactories.keys(),
            factories=extensionFactories,
        )
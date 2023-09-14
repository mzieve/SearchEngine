from typing import Callable, Iterable, Iterator, Optional
from collections import defaultdict
from documents.document import Document
from pathlib import Path
from . import textfiledocument, jsondocument
import json

class DirectoryCorpus:
    def __init__(self,
                 abs_path: Path,
                 file_filter: Callable[[Path], bool] = lambda p: True,
                 factories: Optional[dict[str, Callable[[str], Document]]] = None):
        """
        Initialize a DirectoryCorpus instance.
        
        Args:
            abs_path: Absolute path to the directory containing documents.
            fileFilter: Callable to filter files. By default, accepts all.
            factories: Dictionary mapping file extensions to factory methods for Document instances.
        """
        self.corpus_path = abs_path
        self.file_filter = file_filter
        default_factories = {
            '.txt': textfiledocument.TextFileDocument.load_from,
            '.json': jsondocument.JsonDocument.load_from
        }
        self.factories = factories or defaultdict(lambda: None, default_factories)
        self._documents = {}
        self._read_documents()

    def documents(self) -> Iterable[Document]:
        """Return an iterable over all Document instances in the corpus."""
        return self._documents.values()

    def __iter__(self) -> Iterator[Document]:
        """Make the DirectoryCorpus class iterable over its Document instances."""
        return iter(self.documents())

    def __len__(self) -> int:
        """Return the total number of documents in the corpus."""
        return len(self._documents)

    def get_document(self, docID: int) -> Document:
        """Return a Document instance by its ID."""
        return self._documents.get(docID, None)

    def _read_documents(self) -> None:
        """Read documents from the directory and populate the _documents attribute."""
        next_id = 0
        for f in Path(self.corpus_path).rglob("*"):
            if f.suffix in self.factories and self.file_filter(f):
                if f.suffix == '.json':
                    with open(f, 'r', encoding='utf-8') as json_file:
                        data = json.load(json_file)
                    self._documents[next_id] = self.factories[f.suffix](
                        next_id, data.get("title", ""), data.get("body", ""))
                else:
                    with open(f, 'r', encoding='utf-8') as text_file:
                        content = text_file.read()
                    self._documents[next_id] = self.factories[f.suffix](next_id, f.stem, content)
                next_id += 1

    @staticmethod
    def load_directory(path: Path, extensionFactories: dict[str, Callable[[Path, int], Document]]) -> 'DirectoryCorpus':
        """
        Static method to load a directory and return a DirectoryCorpus instance.
        
        Args:
            path: The directory path.
            extensionFactories: Dictionary mapping file extensions to factory methods.
        """
        return DirectoryCorpus(
            path,
            lambda f: f.suffix in extensionFactories.keys(),
            factories=extensionFactories
        )

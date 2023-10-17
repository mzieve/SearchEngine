from lxml import etree
from pathlib import Path
from typing import Iterable
from .document import Document

class XMLDocument(Document):
    def __init__(self, id: int, title: str, content: str):
        """Initialize an XMLDocument instance."""
        super().__init__(id)
        self._title = title
        self._content = content

    @property
    def title(self) -> str:
        """Return the title of the document."""
        return self._title

    def get_content(self) -> Iterable[str]:
        """Yield the content of the document line by line."""
        for line in self._content.splitlines():
            yield line

    @staticmethod
    def load_from(abs_path: Path, doc_id: int) -> 'XMLDocument':
        """Static method to load an XMLDocument."""
        tree = etree.parse(str(abs_path))
        root = tree.getroot()

        # Define namespace dictionary
        ns = {"tei": "http://www.tei-c.org/ns/1.0"}

        # Extract the title inside the <head> tag
        head_title_element = root.find("./tei:text/tei:body/tei:head/tei:title", namespaces=ns)
        title = head_title_element.text if head_title_element is not None else ""

        # Extract the content
        lines = root.findall(".//tei:text//tei:l", namespaces=ns)
        content = "\n".join(line.text for line in lines if line.text is not None)

        return XMLDocument(doc_id, title, content)
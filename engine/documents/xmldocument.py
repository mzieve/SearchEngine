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
    def load_from(abs_path: Path, doc_id: int) -> "XMLDocument":
        """Static method to load an XMLDocument."""
        tree = etree.parse(str(abs_path))
        root = tree.getroot()

        # Define namespace dictionary
        ns = {"tei": "http://www.tei-c.org/ns/1.0"}

        # Attempt to extract the title using a priority list
        potential_title_tags = [
            "./tei:title",
            "./tei:head/tei:title",
            "./tei:text/tei:body/tei:head/tei:title",
        ]
        title = ""
        for tag in potential_title_tags:
            title_element = root.find(tag, namespaces=ns)
            if title_element is not None and title_element.text:
                title = title_element.text
                break

        # Extract all text content from the XML
        texts = [
            elem.text for elem in tree.iter() if elem.text and not elem.text.isspace()
        ]
        content = "\n".join(texts)

        return XMLDocument(doc_id, title, content)

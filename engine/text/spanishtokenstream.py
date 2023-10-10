from .tokenstream import TokenStream
from typing import Iterator
import spacy

class SpanishTokenStream(TokenStream):
    def __init__(self, source):
        """Constructs a stream over a TextIOWrapper of text."""
        self.source = source
        self.nlp = spacy.load("es_core_news_sm")
        self._open = False

    def __iter__(self) -> Iterator[str]:
        """Returns an iterator over the tokens in the stream."""
        for token in self.source:
            doc = self.nlp(token)
            for tok in doc:
                if len(tok.text) > 0:
                    yield tok.text

    # Resource management functions.
    def __enter__(self):
        self.source.__enter__()

    def __exit__(self):
        if self._open:
            self._open = False
            self.source.__exit__()

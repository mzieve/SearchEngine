from .tokenstream import TokenStream
from typing import Iterator
import spacy

class SpanishTokenStream(TokenStream):
    def __init__(self, source, nlp):
        self.source = source
        self.nlp = nlp

    def __iter__(self) -> Iterator[str]:
        text = ' '.join(self.source) if hasattr(self.source, '__iter__') else self.source.read()
        doc = self.nlp(text)

        for token in doc:
            if len(token.text) > 0:
                yield token.text

    # Resource management functions.
    def __enter__(self):
        self.source.__enter__()

    def __exit__(self):
        if self._open:
            self._open = False
            self.source.__exit__()

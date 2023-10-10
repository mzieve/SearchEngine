from .tokenprocessor import TokenProcessor
import spacy

class SpanishTokenProcessor(TokenProcessor):
    def __init__(self):
        self.nlp = spacy.load("es_core_news_sm")

    def process_token(self, token):
        """Processes tokens into types."""
        return token.lower()

    def normalize_type(self, type_):
        """Normalizes types into terms using spaCy lemmatization."""
        doc = self.nlp(type_)
        if len(doc) > 0:
            return doc[0].lemma_
        return type_
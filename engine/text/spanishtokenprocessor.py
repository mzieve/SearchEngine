from .tokenprocessor import TokenProcessor
import spacy


class SpanishTokenProcessor(TokenProcessor):
    def __init__(self):
        self.nlp = spacy.load("es_core_news_sm")

    def process_token(self, token):
        """Processes tokens into types."""
        doc = self.nlp(token)
        processed_tokens = []

        for tok in doc:
            if tok.is_alpha:
                alpha_text = "".join(filter(str.isalnum, tok.text.lower()))
                if alpha_text:
                    processed_tokens.append(alpha_text)

        return processed_tokens

    def normalize_type(self, type_):
        """Normalizes types into terms using spaCy lemmatization."""
        doc = self.nlp(type_)
        if len(doc) > 0:
            return doc[0].lemma_
        return type_

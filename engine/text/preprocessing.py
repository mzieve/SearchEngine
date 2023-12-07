from engine.text import (
    BasicTokenProcessor,
    SpanishTokenProcessor,
    EnglishTokenStream,
    SpanishTokenStream,
)
from engine.indexing import Index, PositionalInvertedIndex
from langdetect import detect  # type: ignore
import config
import spacy


class Preprocessing:
    def __init__(self, text=None):
        self.text = text
        self.p_i_index = PositionalInvertedIndex()
        self.nlp = spacy.load("es_core_news_sm")

    def detect_language(self, text):
        """Detects the language of the provided text."""
        detected_lang = detect(text)
        return {"en": "english", "es": "spanish"}.get(detected_lang, "english")

    def dic_process_position(self, document, progress_callback=None):
        """Position each document based on the detected language"""
        eng_processor = BasicTokenProcessor()
        es_processor = SpanishTokenProcessor()

        """
        if config.LANGUAGE == "english":
            tokens = EnglishTokenStream(document.get_content())
            processor = BasicTokenProcessor()
        elif config.LANGUAGE == "spanish":
            tokens = SpanishTokenStream(document.get_content(), nlp=self.nlp)
            processor = SpanishTokenProcessor()
        """

        tokens = EnglishTokenStream(document.get_content())
        processor = BasicTokenProcessor()

        position = 0
        for token in tokens:
            position += 1
            tok_types = processor.process_token(token)

            for tok_type in tok_types:
                term = processor.normalize_type(tok_type)
                self.p_i_index.addTerm(term, document.id, position)

        # Update the progress after processing the document, if callback provided
        if progress_callback:
            progress_callback()

    def process(self, query):
        """Processes the text based on its detected language."""
        if config.LANGUAGE == "english":
            return self.proc_eng_query(query)
        elif config.LANGUAGE == "spanish":
            return self.proc_es_query(query)
        else:
            raise ValueError(f"Unsupported language: {config.LANGUAGE}")

    def proc_eng_query(self, query):
        """Processes English words using BasicTokenProcessor and EnglishTokenStream."""
        processor = BasicTokenProcessor()
        tokens = EnglishTokenStream([query])

        processed_query = []
        for token in tokens:
            tok_types = processor.process_token(token)

            for tok_type in tok_types:
                term = processor.normalize_type(tok_type)
                processed_query.append(term)

        return " ".join(processed_query)

    def proc_es_query(self, query):
        """Processes Spanish words using SpanishTokenProcessor and SpanishTokenStream."""
        processor = SpanishTokenProcessor()
        tokens = SpanishTokenStream([query], nlp=self.nlp)

        processed_query = []
        for token in tokens:
            tok_types = processor.process_token(token)

            for tok_type in tok_types:
                term = processor.normalize_type(tok_type)
                processed_query.append(term)

        return " ".join(processed_query)

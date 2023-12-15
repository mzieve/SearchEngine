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
        self.nlp = spacy.load("es_core_news_sm")
        self.p_i_index = PositionalInvertedIndex()
        self.eng_processor = BasicTokenProcessor()
        #self.eng_processor = SpanishTokenProcessor()

    def detect_language(self, text):
        """Detects the language of the provided text."""
        detected_lang = detect(text)
        return {"en": "english", "es": "spanish"}.get(detected_lang, "english")

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

    def dic_process_position(self, document, progress_callback=None):
        """Yield each token with its position from the document."""

        tokens = EnglishTokenStream(document.get_content())

        position = 0
        for token in tokens:
            position += 1
            tok_types = self.eng_processor.process_token(token)

            for tok_type in tok_types:
                term = self.eng_processor.normalize_type(tok_type)
                yield (term, document.id, position)

            if progress_callback:
                progress_callback()

    def process_merged(self, file_path):
        """Reconstructs the index from a merged postings file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                term, postings_str = line.strip().split(": ")
                postings_list = postings_str.split(";")
                for posting_str in postings_list:
                    doc_id, positions_str = posting_str.split("[", 1)  
                    doc_id = doc_id.strip(",")  
                    positions_str = positions_str.strip(']') 
                    positions_str = positions_str.replace("'", "") 
                    positions = list(map(int, positions_str.split(','))) 

                    for position in positions:
                        self.p_i_index.addTerm(term, int(doc_id), position)

        return self.p_i_index

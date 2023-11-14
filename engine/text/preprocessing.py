import struct

from engine.text import (
    BasicTokenProcessor,
    SpanishTokenProcessor,
    EnglishTokenStream,
    SpanishTokenStream,
)
from engine.indexing import Index, PositionalInvertedIndex, DiskIndexWriter, DiskPositionalIndex
from langdetect import detect  # type: ignore
from math import sqrt
import config
import spacy
import os


class Preprocessing:
    def __init__(self, text=None):
        self.text = text
        self.p_i_index = PositionalInvertedIndex()
        self.nlp = spacy.load("es_core_news_sm")
        #Find a way to make this path relative.
        self.on_disk_index_path = r"C:\Users\seanl\OneDrive\Documents\University_Documents\Our_Best_Search_Engine\SearchEngine\data"
        self.d_i_writer = DiskIndexWriter(self.on_disk_index_path)
        self.d_i_index = DiskPositionalIndex(self.on_disk_index_path, self.on_disk_index_path)

    def detect_language(self, text):
        """Detects the language of the provided text."""
        detected_lang = detect(text)
        return {"en": "english", "es": "spanish"}.get(detected_lang, "english")

    def dic_process_position(self, corpus, progress_callback=None):
        """Position each document based on the detected language"""
        eng_processor = BasicTokenProcessor()
        es_processor = SpanishTokenProcessor()
        doc_Weights_file_path = os.path.join(self.on_disk_index_path, "docWeights.bin")
        doc_Weights_file = open(doc_Weights_file_path, "wb")
        #Does this loop go through the docs in Doc ID order?
        for i, doc_path in enumerate(corpus):
            #For each doc:
            if config.LANGUAGE == "english":
                tokens = EnglishTokenStream(doc_path.get_content())
                processor = eng_processor
            elif config.LANGUAGE == "spanish":
                tokens = SpanishTokenStream(doc_path.get_content(), nlp=self.nlp)
                processor = es_processor

            position = 0
            #Record tftd values for each term in this document.
            tftd = dict()
            for token in tokens:
                position += 1
                tok_types = processor.process_token(token)

                for tok_type in tok_types:
                    term = processor.normalize_type(tok_type)
                    self.p_i_index.addTerm(term, doc_path.id, position)
                    if term not in tftd:
                        tftd[term] = 1
                    else:
                        tftd[term] += 1
            tftd_sq_sum = 0
            for term, freq in tftd.items():
                tftd_sq_sum += freq ** 2
            euc_len = float(sqrt(tftd_sq_sum))
            packed_euc_len = struct.pack("f", euc_len)
            doc_Weights_file.write(packed_euc_len)
            # After processing each document, update the progress.
            if progress_callback:
                progress_callback(i + 1)
        doc_Weights_file.close()
        #get the current working directory
        #cwd = os.getcwd()

        #The positional inverted index has all the info we need. Write it to disk.
        self.d_i_writer.writeIndex(self.p_i_index, self.on_disk_index_path)
        # on_disk_index_path = "C:\Users\seanl\OneDrive\Documents\University_Documents\Our_Best_Search_Engine\SearchEngine\data"
        return self.p_i_index.getVocabulary()

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

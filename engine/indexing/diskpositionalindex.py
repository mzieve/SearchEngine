from typing import Iterable
from .postings import Posting
from config import DOC_WEIGHTS_FILE_PATH
import struct
import sqlite3
import os


class DiskPositionalIndex:
    def __init__(self, db_path, postings_file_path):
        """Initialize the DiskPositionalIndex. Connects to the SQLite database and loads term start positions from it."""
        self.postings_file_path = postings_file_path
        self.db_conn = sqlite3.connect(db_path, check_same_thread=False)
        self.db_cursor = self.db_conn.cursor()
        self.term_start_positions = self._start_positions()
        self.is_phrase_query = False 
        self.total_docs = self.get_total_docs()
        self.avg_doc_length = self.calculate_average_document_length() if self.total_docs > 0 else 0

    def set_phrase_query(self, is_phrase_query):
        """Sets the flag indicating whether the current query is a phrase query."""
        self.is_phrase_query = is_phrase_query

    def _start_positions(self):
        """Retrieves the start positions of each term from the database."""
        term_start_positions = {}
        self.db_cursor.execute("SELECT term, position FROM term_positions")
        for term, position in self.db_cursor.fetchall():
            term_start_positions[term] = position
        return term_start_positions

    def _start_position(self, term: str):
        """Retrieves the start position of a given term."""
        return self.term_start_positions.get(term, None)

    def _read_positions(self, postings_file, tftd):
        """Reads the positions of terms in a document from the postings file."""
        last_position = 0
        positions = []
        for _ in range(tftd):
            position_gap = struct.unpack("I", postings_file.read(4))[0]
            position = last_position + position_gap
            positions.append(position)
            last_position = position
        return positions

    def getPostings(self, term: str) -> Iterable[Posting]:
        """Retrieves postings for a given term, either with positions (for phrase queries) or without (for non-phrase queries)."""
        if self.is_phrase_query:
            return self.positionPostings(term)
        else:
            return self.skipPostings(term)
    
    def getVocabulary(self):
        """Retrieves the full list of indexed terms (vocabulary) from the database."""
        self.db_cursor.execute("SELECT DISTINCT term FROM term_positions ORDER BY term")
        return [row[0] for row in self.db_cursor.fetchall()]

    def positionPostings(self, term: str) -> Iterable[Posting]:
        """Retrieves postings with positions for a given term."""
        start_position = self._start_position(term)
        if start_position is None:
            return []

        postings = []
        with open(self.postings_file_path, "rb") as postings_file:
            postings_file.seek(start_position)
            dft = struct.unpack("I", postings_file.read(4))[0]
            last_doc_id = 0
            for _ in range(dft):
                doc_gap = struct.unpack("I", postings_file.read(4))[0]
                doc_id = last_doc_id + doc_gap
                tftd = struct.unpack("I", postings_file.read(4))[0]
                positions = self._read_positions(postings_file, tftd)
                postings.append(Posting(doc_id, positions))
                last_doc_id = doc_id

        return postings

    def skipPostings(self, term: str) -> Iterable[Posting]:
        """Retrieves postings without positions for a given term."""
        start_position = self._start_position(term)
        if start_position is None:
            return []

        postings = []
        with open(self.postings_file_path, "rb") as postings_file:
            postings_file.seek(start_position)
            dft = struct.unpack("I", postings_file.read(4))[0]
            last_doc_id = 0
            for _ in range(dft):
                doc_gap = struct.unpack("I", postings_file.read(4))[0]
                doc_id = last_doc_id + doc_gap
                tftd = struct.unpack("I", postings_file.read(4))[0]
                postings_file.seek(tftd * 4, os.SEEK_CUR)
                postings.append(Posting(doc_id, 0))
                last_doc_id = doc_id

        return postings

    def get_term_frequency(self, term: str, doc_id: int) -> int:
        """Retrieves the term frequency (tf) for a specific term in a specific document."""
        start_position = self._start_position(term)
        if start_position is None:
            return 0

        with open(self.postings_file_path, "rb") as postings_file:
            postings_file.seek(start_position)
            dft = struct.unpack("I", postings_file.read(4))[0]
            last_doc_id = 0
            for _ in range(dft):
                doc_gap = struct.unpack("I", postings_file.read(4))[0]
                current_doc_id = last_doc_id + doc_gap
                tftd = struct.unpack("I", postings_file.read(4))[0]
                # If the current doc_id is the one we're looking for, return its tf
                if current_doc_id == doc_id:
                    return tftd
                # Skip the positions data for this document
                postings_file.seek(tftd * 4, os.SEEK_CUR)
                last_doc_id = current_doc_id
        # If we've gone through all postings and haven't found the doc_id, return 0
        return 0

    def get_doc_weights(self) -> dict[int, float]:
        """Loads the document weights (Euclidean lengths) from the specified file."""
        doc_weights = {}
        try:
            with open(DOC_WEIGHTS_FILE_PATH, 'rb') as doc_weights_file:
                doc_id = 0
                while True:
                    doc_weight_data = doc_weights_file.read(8) 
                    if not doc_weight_data:
                        break
                    L_d, = struct.unpack('d', doc_weight_data)
                    doc_weights[doc_id] = L_d
                    doc_id += 1
            return doc_weights
        except FileNotFoundError:
            print(f"File not found: {DOC_WEIGHTS_FILE_PATH}")
            return {}

    def calculate_average_document_length(self):
        """Calculates the average document length for the corpus."""
        doc_weights = self.get_doc_weights()
        if not doc_weights:
            return 0
        total_length = sum(doc_weights.values())
        return total_length / self.total_docs if self.total_docs > 0 else 0
    
    def get_total_docs(self):
        """Retrieve the total number of documents in the index."""
        self.db_cursor.execute("SELECT COUNT(*) FROM document_metadata")
        result = self.db_cursor.fetchone()
        return result[0] if result else 0

    def close(self):
        self.db_conn.close()


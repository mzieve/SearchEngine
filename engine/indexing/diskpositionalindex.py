import os
import struct
import sqlite3
from typing import Iterable
from .index import Index
from .postings import Posting

class DiskPositionalIndex:
    def __init__(self, db_path, postings_file_path):
        """Initialize the DiskPositionalIndex. Connects to the SQLite database and loads term start positions from it."""
        self.postings_file_path = postings_file_path
        self.db_conn = sqlite3.connect(db_path, check_same_thread=False)
        self.db_cursor = self.db_conn.cursor()
        self.term_start_positions = self._start_positions()
        self.is_phrase_query = False  # Add this line

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
            position_gap = struct.unpack('I', postings_file.read(4))[0]
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


    def positionPostings(self, term: str) -> Iterable[Posting]:
        """ Retrieves postings with positions for a given term."""
        start_position = self._start_position(term)
        if start_position is None:
            return []

        postings = []
        with open(self.postings_file_path, 'rb') as postings_file:
            postings_file.seek(start_position)
            dft = struct.unpack('I', postings_file.read(4))[0]
            last_doc_id = 0
            for _ in range(dft):
                doc_gap = struct.unpack('I', postings_file.read(4))[0]
                doc_id = last_doc_id + doc_gap
                tftd = struct.unpack('I', postings_file.read(4))[0]
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
        with open(self.postings_file_path, 'rb') as postings_file:
            postings_file.seek(start_position)
            dft = struct.unpack('I', postings_file.read(4))[0]
            last_doc_id = 0
            for _ in range(dft):
                doc_gap = struct.unpack('I', postings_file.read(4))[0]
                doc_id = last_doc_id + doc_gap
                tftd = struct.unpack('I', postings_file.read(4))[0]
                postings_file.seek(tftd * 4, os.SEEK_CUR)
                postings.append(Posting(doc_id, 0))
                last_doc_id = doc_id

        return postings

    def close(self):
        self.db_conn.close()
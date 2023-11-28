from collections import defaultdict
import struct
import sqlite3
import math
import os

class DiskIndexWriter:
    def __init__(self, db_path, index):
        """Initialize the DiskIndexWriter with the specified database path and in-memory index."""
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_conn = sqlite3.connect(db_path)
        self.db_cursor = self.db_conn.cursor()
        self.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS term_positions (
                term TEXT PRIMARY KEY,
                position INTEGER
            )''')
        self.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_metadata (
                doc_id INTEGER PRIMARY KEY,
                title TEXT
            )''')
        self.db_conn.commit()
        self.index = index 

    def write_index(self, postings_file_path, doc_weights_file_path, corpus):
        """Writes the index to the disk, including term positions, document weights, and document metadata."""
        os.makedirs(os.path.dirname(postings_file_path), exist_ok=True)
        os.makedirs(os.path.dirname(doc_weights_file_path), exist_ok=True)
        self.db_cursor.execute('DELETE FROM term_positions')
        self.db_conn.commit()
        doc_lengths = self.calculate_document_lengths()
        self.write_doc_weights(doc_lengths, doc_weights_file_path)
        
        with open(postings_file_path, 'wb') as postings_file:
            for term in self.index.getVocabulary():
                postings_list = self.index.getPostings(term)
                self.db_cursor.execute('INSERT INTO term_positions (term, position) VALUES (?, ?)',
                                       (term, postings_file.tell()))

                df, postings_data = self._encode_postings(postings_list)
                postings_file.write(df)
                postings_file.write(postings_data)

        for doc_id, document in enumerate(corpus.documents()):
            self.db_cursor.execute('INSERT INTO document_metadata (doc_id, title) VALUES (?, ?)',
                                   (doc_id, document.title))

        self.db_conn.commit()

    def _encode_postings(self, postings_list):
        """Encodes the postings list using gap encoding."""
        df = struct.pack('I', len(postings_list))
        postings_data = b''
        last_doc_id = 0
        for posting in postings_list:  
            doc_gap = posting.doc_id - last_doc_id 
            last_doc_id = posting.doc_id
            postings_data += struct.pack('I', doc_gap)
            postings_data += struct.pack('I', len(posting.positions))  
            last_position = 0
            for position in posting.positions:  
                position_gap = position - last_position
                last_position = position
                postings_data += struct.pack('I', position_gap)
        return df, postings_data

    def calculate_document_lengths(self) -> dict[int, float]:
        """Calculates the Euclidean length (L_d) for all documents in the index."""
        document_lengths = defaultdict(float)
        for term in self.index.getVocabulary(): 
            postings = self.index.getPostings(term)  
            for posting in postings:
                tf = len(posting.positions)
                document_lengths[posting.doc_id] += tf ** 2

        for doc_id in document_lengths:
            document_lengths[doc_id] = math.sqrt(document_lengths[doc_id])

        return document_lengths

    def write_doc_weights(self, doc_lengths: dict[int, float], doc_weights_file_path: str):
        """Writes the document weights (Euclidean lengths) to the specified file."""
        with open(doc_weights_file_path, 'wb') as doc_weights_file:
            for doc_id in sorted(doc_lengths.keys()):
                L_d = doc_lengths[doc_id]
                doc_weights_file.write(struct.pack('d', L_d))

    def close(self):
        self.db_conn.close()
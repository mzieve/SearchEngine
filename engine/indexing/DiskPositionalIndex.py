from typing import Iterable
from .postings import Posting
from .index import Index
import sqlite3
import struct
class DiskPositionalIndex(Index):
    """Implements a positional inverted index on disk."""

    def __init__(self, path):
        """Constructs an empty index"""
        self.path = path
        conn = sqlite3.connect("../../data/postings_start.db")
        self.cursor = conn.cursor()

    def getPostings(self, term: str) -> Iterable[Posting]:
        """Returns a list of Postings for all documents that contain the given term."""
        postings = []
        # 1. Use your database to load the byte position of where the term's postings begin.
        self.cursor.execute("SELECT postings_start FROM beginnings WHERE term = '{term}'")
        postings_start = self.cursor.fetchall()
        # 2. Using your already-opened postings.bin file, seek to the position of the term.
        postings_file_path = self.path + "\postings.bin"
        postings_file = open(postings_file_path, "rb")
        postings_file.seek(postings_start)
        """
        3. Using readInt (Java), read() w/ struct.unpack (Python), or .read() (C++), read dft, 
            then docid gap, then tftd, then position gap, etc. etc. As values are read, construct 
            in-memory Posting objects to store the information, then return a List of Postings 
            when you have read everything you need from disk (for this term only).
        """
        packed_dft = postings_file.read([8])
        dft = struct.unpack("i", packed_dft)
        prev_doc_id = 0
        for pstng in range(dft):
            packed_d_id_gap = postings_file.read([8])
            doc_id_gap = struct.unpack("i", packed_d_id_gap)
            doc_id = prev_doc_id + doc_id_gap
            packed_tftd = postings_file.read([8])
            tftd = struct.unpack("i", packed_tftd)
            prev_position = 0
            positions = []
            for postn in range(tftd):
                packed_p_gap = postings_file.read([8])
                position_gap = struct.unpack("i", packed_p_gap)
                position = prev_position + position_gap
                positions.append(position)
            posting = Posting(doc_id, positions[0])
            posting.positions.extend(positions[1:])
            postings.append(posting)
        return postings
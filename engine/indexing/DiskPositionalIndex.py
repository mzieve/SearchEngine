from io import TextIOWrapper
from typing import Iterable, BinaryIO
from .postings import Posting
from .index import Index
import sqlite3
import struct
import os
class DiskPositionalIndex(Index):
    """Implements a positional inverted index on disk."""

    def __init__(self, postings_db_files_path):
        """Constructs an empty index"""
        self.postings_path = postings_db_files_path
        db_file_name = os.path.join(postings_db_files_path, "postings_start.db")
        conn = sqlite3.connect(db_file_name, check_same_thread=False)
        self.cursor = conn.cursor()

    def goto_term(self, term: str):
        # 1. Use your database to load the byte position of where the term's postings begin.
        sql = "SELECT postings_start FROM beginnings WHERE term='{}'".format(term)
        self.cursor.execute(sql)
        postings_start = self.cursor.fetchone()[0]
        # 2. Using your already-opened postings.bin file, seek to the position of the term.
        postings_file_path = os.path.join(self.postings_path, "postings.bin")
        postings_file = open(postings_file_path, "rb")
        postings_file.seek(postings_start)
        return postings_file
    def getPostings(self, term: str, need_pos: bool) -> Iterable[Posting]:
        """Returns a list of Postings for all documents that contain the given term."""
        postings_file = self.goto_term(term)
        """
        3. Using readInt (Java), read() w/ struct.unpack (Python), or .read() (C++), read dft, 
            then docid gap, then tftd, then position gap, etc. etc. As values are read, construct 
            in-memory Posting objects to store the information, then return a List of Postings 
            when you have read everything you need from disk (for this term only).
            
            Only read positions when need_pos argument is True, otherwise, skip over them.
        """
        if need_pos:
            return self.getPostingsWithPositions(term, postings_file)
        else:
            return self.getPostingsWithoutPositions(term, postings_file)

    def getPostingsWithPositions(self, term: str, postings_file: BinaryIO):
        postings = []
        packed_dft = postings_file.read(4)
        dft = struct.unpack("i", packed_dft)[0]
        prev_doc_id = 0
        for pstng in range(dft):
            packed_d_id_gap = postings_file.read(4)
            doc_id_gap = struct.unpack("i", packed_d_id_gap)[0]
            doc_id = prev_doc_id + doc_id_gap
            packed_tftd = postings_file.read(4)
            tftd = struct.unpack("i", packed_tftd)[0]
            prev_position = 0
            positions = []
            for postn in range(tftd):
                packed_p_gap = postings_file.read(4)
                position_gap = struct.unpack("i", packed_p_gap)[0]
                position = prev_position + position_gap
                positions.append(position)
            posting = Posting(doc_id, positions[0])
            posting.positions.extend(positions[1:])
            postings.append(posting)
        return postings

    def getPostingsWithoutPositions(self, term: str, postings_file: BinaryIO):
        postings = []
        packed_dft = postings_file.read(4)
        dft = struct.unpack("i", packed_dft)[0]
        prev_doc_id = 0
        for pstng in range(dft):
            packed_d_id_gap = postings_file.read(4)
            doc_id_gap = struct.unpack("i", packed_d_id_gap)[0]
            doc_id = prev_doc_id + doc_id_gap
            packed_tftd = postings_file.read(4)
            tftd = struct.unpack("i", packed_tftd)[0]
            postings_file.seek(4 * tftd, 1)
            posting = Posting(doc_id, -1)
            postings.append(posting)
        return postings


    def getVocabulary(self) -> list[str]:
        pass
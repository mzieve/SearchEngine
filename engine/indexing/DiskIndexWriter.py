import struct

from .postionalinvertedindex import PositionalInvertedIndex
import sqlite3
class DiskIndexWriter:
    def __init__(self):
        conn = sqlite3.connect("../../data/postings_start.db")
        self.cursor = conn.cursor()

    def writeIndex(self, p_i_index, on_disk_index_path):
        """
        Writing the on-disk index.
        """
        # Creating / opening a file in binary mode in the specified path to write the postings of the on-disk index.
        postings_file_path = on_disk_index_path + "\postings.bin"
        postings_file = open(postings_file_path, "rb")
        vocab = p_i_index.getVocabulary()
        for term in vocab:
            postings_start = postings_file.tell()
            postings = p_i_index.getPostings(term)
            dft = len(postings)
            packed_dft = struct.pack("i", dft)
            print("packed_dft", packed_dft)
            # Write to disk.
            postings_file.write(packed_dft)
            prev_doc_id = 0
            for posting in postings:
                doc_id_gap = posting.doc_id - prev_doc_id
                prev_doc_id = posting.doc_id
                tftd = len(posting.positions)
                packed_d_id_gap = struct.pack("i", doc_id_gap)
                packed_tftd = struct.pack("i", tftd)
                # Write to disk.
                postings_file.write(packed_d_id_gap)
                postings_file.write(packed_tftd)
                prev_position = 0
                for position in posting.positions:
                    position_gap = position - prev_position
                    prev_position = position
                    # Write to disk.
                    packed_p_gap = struct.pack("i", position_gap)
                    postings_file.write(packed_p_gap)
            # Save byte position of start of this term's postings list in SQLite database.
            self.cursor.execute(
                f"""
                INSERT INTO beginnings
                VALUES ({term}, {postings_start})
                """)
        postings_file.close()
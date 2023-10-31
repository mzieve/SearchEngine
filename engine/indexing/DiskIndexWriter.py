import struct

from .postionalinvertedindex import PositionalInvertedIndex
import sqlite3
class DiskIndexWriter:
    def __init__(self):
        pass

    def writeIndex(self, p_i_index, on_disk_index_path):
        """
        Writing the on-disk index.
        """
        # Creating / opening a file in binary mode in the specified path to write the positngs of the on-disk index.
        postings_file_path = on_disk_index_path + "\postings.bin"
        postings_file = open(postings_file_path, "rb")
        vocab = p_i_index.getVocabulary()
        for term in vocab:
            postings = p_i_index.getPostings(term)
            dft = len(postings)
            packed_dft = struct.pack("i", dft)
            print("packed_dft", packed_dft)
            # Write to disk.
            prev_doc_id = 0
            for posting in postings:
                doc_id_gap = posting.doc_id - prev_doc_id
                tftd = len(postings.positions)
                # Write to disk.
                prev_position = 0
                for position in postings.positions:
                    position_gap = position - prev_position
                    # Write to disk.
            # Save byte position of start of this term's postings in SQLite database.
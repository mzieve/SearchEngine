from engine.indexing import DiskIndexWriter, PositionalInvertedIndex, Posting
from engine.text import Preprocessing
from config import DB_PATH, POSTINGS_FILE_PATH, DOC_WEIGHTS_FILE_PATH, DATA_DIR
from pympler import asizeof
from queue import PriorityQueue
from collections import defaultdict
import json
import os
import heapq
import config


class SPIMI:
    def __init__(self, output_dir, corpus):
        self.output_dir = output_dir
        self.corpus = corpus
        self.in_memory_index = {}
        self.file_counter = 0
        self.preprocessing = Preprocessing()
        self.p_i_index = PositionalInvertedIndex()
        os.makedirs(self.output_dir, exist_ok=True)

    def spimi_index(self, progress_callback=None):
        total_positions = 0
        total_memory = 0

        for i, document in enumerate(self.corpus):
            total_memory += 4
            for term, doc_id, position in self.preprocessing.dic_process_position(document):
                self.p_i_index.addTerm(term, doc_id, position)
                total_memory += 5

                if self.memory_limit(total_memory):
                    self.memory_index()
                    total_memory = 0
                    self.p_i_index.clear()

            if progress_callback:
                progress_callback(i, len(self.corpus))

        self.memory_index()
        self.merge_files()

        print("SPIMI indexing completed.")

    def memory_index(self):
        """Sorts the in-memory index and writes it to disk."""
        file_path = os.path.join(self.output_dir, f"bucket_{self.file_counter}.txt")
        with open(file_path, "w", encoding='utf-8') as file:
            formatted_index = self.p_i_index.export_sorted_index()
            file.write(formatted_index)

        self.file_counter += 1
        self.p_i_index.clear()

    def merge_files(self):
        print("Merging Files...")

        # Open file-read streams
        file_streams = [open(os.path.join(self.output_dir, f"bucket_{i}.txt"), "r", encoding='utf-8') for i in range(self.file_counter)]

        # Initialize priority queue with the first term and its postings from each file
        pq = PriorityQueue()
        for i, stream in enumerate(file_streams):
            line = stream.readline().strip()
            if line:
                term, postings = line.split(": ", 1)
                for posting in postings.split(";"):
                    doc_id, positions = posting.split(",", 1)
                    pq.put((term, int(doc_id), positions, i))

        # Open file-write stream for the final merged postings file
        with open(os.path.join(self.output_dir, "merged_postings.txt"), "w", encoding='utf-8') as merged_file:
            current_term = None
            current_postings = defaultdict(list)

            while not pq.empty():
                term, doc_id, positions, file_idx = pq.get()
                positions_set = sorted(set(map(int, positions.strip('[]').split(','))))

                if term != current_term and current_term is not None:
                    # Write postings for the previous term
                    merged_postings = '; '.join(f"{doc_id},{pos_list}" for doc_id, pos_list in current_postings.items())
                    merged_file.write(f"{current_term}: {merged_postings}\n")
                    current_postings = defaultdict(list)

                current_term = term
                current_postings[doc_id].extend(positions_set)

                # Read next line from the file that the term came from
                next_line = file_streams[file_idx].readline().strip()
                if next_line:
                    next_term, next_postings = next_line.split(": ", 1)
                    for posting in next_postings.split(";"):
                        next_doc_id, next_positions = posting.split(",", 1)
                        pq.put((next_term, int(next_doc_id), next_positions, file_idx))

            # Write postings for the last term
            if current_term is not None:
                merged_postings = '; '.join(f"{doc_id},{pos_list}" for doc_id, pos_list in current_postings.items())
                merged_file.write(f"{current_term}: {merged_postings}\n")

        # Close all file streams
        for stream in file_streams:
            stream.close()

        print("Merge complete.")

    def memory_limit(self, total_memory):
        MEMORY_LIMIT = 250000  
        return total_memory > MEMORY_LIMIT
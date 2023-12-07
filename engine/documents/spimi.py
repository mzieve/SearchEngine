from engine.indexing import DiskIndexWriter, PositionalInvertedIndex, Posting
from engine.text import Preprocessing
from config import DB_PATH, POSTINGS_FILE_PATH, DOC_WEIGHTS_FILE_PATH, DATA_DIR
import json
import os
import glob
import heapq
import psutil
import io
import config
import pickle
import sys


class SPIMI:
    def __init__(self, output_dir, corpus):
        self.output_dir = output_dir
        self.corpus = corpus
        self.in_memory_index = {}
        self.file_counter = 0
        self.preprocessing = Preprocessing()
        os.makedirs(self.output_dir, exist_ok=True)

    def spimi_index(self, progress_callback=None):
        for i, document in enumerate(self.corpus):
            self.process_document(
                document,
                progress_callback=lambda: progress_callback(i, len(self.corpus)),
            )
            if self.memory_is_exhausted():
                self.sort_and_write_to_disk()

        # Write any remaining data to disk
        if self.in_memory_index:
            self.sort_and_write_to_disk()

        final_merged_index = self.merge_files()

        # Convert final_merged_index dictionary into PositionalInvertedIndex
        final_index = PositionalInvertedIndex()
        for term, postings in final_merged_index.items():
            for doc_id, position in postings:
                final_index.addTerm(term, doc_id, position)

        # Now pass final_index to DiskIndexWriter
        disk_index_writer = DiskIndexWriter(DB_PATH, final_index)
        disk_index_writer.write_index(
            POSTINGS_FILE_PATH, DOC_WEIGHTS_FILE_PATH, self.corpus
        )
        disk_index_writer.close()

        print("SPIMI indexing completed.")

    def process_document(self, document, progress_callback=None):
        # Document processing and position extraction
        self.preprocessing.dic_process_position(document, progress_callback)
        for term, postings in self.preprocessing.p_i_index.index.items():
            for posting in postings:
                # Handle multiple positions per posting
                for position in posting.positions:
                    self.add_to_index(term, posting.doc_id, position)

    def add_to_index(self, term, doc_id, position):
        # Considering alternative data structures for memory efficiency
        if term not in self.in_memory_index:
            self.in_memory_index[term] = []
        # Store as a list initially and deduplicate during merge
        self.in_memory_index[term].append((doc_id, position))

    def sort_and_write_to_disk(self):
        """Sorts the in-memory index and writes it to disk."""
        sorted_terms = sorted(self.in_memory_index.keys())
        file_path = os.path.join(self.output_dir, f"spimi_{self.file_counter}.txt")
        with open(file_path, "wb") as file:
            for term in sorted_terms:
                # Convert list to set for deduplication before dumping
                postings = sorted(set(self.in_memory_index[term]))
                pickle.dump((term, postings), file)
        self.file_counter += 1
        self.in_memory_index.clear()

    def merge_files(self):
        index_files = glob.glob(os.path.join(self.output_dir, "spimi_*.txt"))
        streams = [open(file, "rb") for file in index_files]
        pq = []
        current_terms = [None] * len(streams)  # To keep track of the current state

        # Initial loading of terms from each stream
        for i, stream in enumerate(streams):
            try:
                current_terms[i] = pickle.load(stream)
                heapq.heappush(pq, (current_terms[i][0], i))
            except EOFError:
                pass

        final_index_path = os.path.join(self.output_dir, "spimi.txt")
        with open(final_index_path, "wb") as final_index_file:
            while pq:
                smallest_term, stream_index = heapq.heappop(pq)
                lists_to_merge = [current_terms[stream_index][1]]

                # Merge postings lists for the smallest term
                while pq and pq[0][0] == smallest_term:
                    _, next_stream_index = heapq.heappop(pq)
                    lists_to_merge.append(current_terms[next_stream_index][1])

                merged_postings = self.merge_postings(lists_to_merge)
                pickle.dump((smallest_term, merged_postings), final_index_file)

                # Read next term from the stream that just got used
                try:
                    current_terms[stream_index] = pickle.load(streams[stream_index])
                    heapq.heappush(pq, (current_terms[stream_index][0], stream_index))
                except EOFError:
                    pass

        for stream in streams:
            stream.close()

        final_merged_index = {}
        with open(final_index_path, "rb") as final_index_file:
            while True:
                try:
                    term, postings = pickle.load(final_index_file)
                    final_merged_index[term] = postings
                except EOFError:
                    break
        return final_merged_index

    def merge_postings(self, postings_lists):
        # Optimized to avoid creating an intermediate list
        merged_postings_set = set()
        for postings in postings_lists:
            merged_postings_set.update(postings)
        return sorted(merged_postings_set)

    def memory_is_exhausted(self):
        MEMORY_LIMIT = 50000000 
        estimated_memory_usage = self.estimate_memory_usage()
        return estimated_memory_usage > MEMORY_LIMIT

    def estimate_memory_usage(self):
        # New implementation for a more accurate estimation
        return self.estimate_dict_memory_usage(self.in_memory_index)

    def estimate_dict_memory_usage(self, dictionary):
        size = sys.getsizeof(dictionary)
        for key, value in dictionary.items():
            size += sys.getsizeof(key)
            size += sys.getsizeof(value)  # Assuming value is a set
            if isinstance(value, set):
                size += sum(sys.getsizeof(item) for item in value)
        return size

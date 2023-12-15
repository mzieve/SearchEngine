from engine.indexing import PositionalInvertedIndex
from engine.text import Preprocessing
from config import WEIGHTS_DIR, BUCKET_DIR, DB_PATH, POSTINGS_DIR
import struct
import sqlite3
import math
import os
import heapq

class Posting:
    def __init__(self, term, file_index, postings_data):
        self.term = term
        self.file_index = file_index
        self.postings_data = postings_data
    def __lt__(self, other):
        return self.term < other.term


class SPIMI:
    def __init__(self, corpus):
        """Initialize the DiskIndexWriter with the specified database path and in-memory index."""
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.db_conn = sqlite3.connect(DB_PATH)
        self.db_cursor = self.db_conn.cursor()
        self.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS term_positions (
                term TEXT PRIMARY KEY,
                position INTEGER
            )''')
        self.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_metadata (
                doc_id INTEGER PRIMARY KEY,
                title TEXT,
                doc_length INTEGER
            )''')
        self.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS corpus_stats (
                stat_name TEXT PRIMARY KEY,
                value INTEGER
            )''')
        self.db_conn.commit()

        os.makedirs(BUCKET_DIR, exist_ok=True)
        self.preprocessing = Preprocessing()
        self.p_i_index = PositionalInvertedIndex()
        self.corpus = corpus
        self.in_memory_index = {}
        self.file_counter = 0
        self.uniq_terms = 0

    def batch_insert_document_metadata(self, documents):
        # 'documents' is now a list of tuples (doc_id, title, doc_length)
        self.db_cursor.executemany('INSERT INTO document_metadata (doc_id, title, doc_length) VALUES (?, ?, ?)', documents)
        self.db_conn.commit()

    def spimi_index(self, progress_callback=None):
        """Creates the positional inverted index using SPIMI."""
        print("SPIMI indexing...")
        total_memory = 0
        num_docs = 36803

        document_metadata = []
        doc_term_freq = {}
        total_tokens = 0

        # Single loop for indexing and metadata handling
        for i, document in enumerate(self.corpus.load_documents_generator()):
            doc_id = document.id
            doc_length = 0
            doc_term_freq[doc_id] = {}

            # Process each term in the document
            for term, _, position in self.preprocessing.dic_process_position(document):
                self.p_i_index.addTerm(term, doc_id, position)
                total_memory += 5
                doc_term_freq[doc_id][term] = doc_term_freq[doc_id].get(term, 0) + 1
                doc_length += 1

                # Check memory limit
                if self.memory_limit(total_memory):
                    self.memory_index()
                    total_memory = 0
                    self.p_i_index.clear()

            # Accumulate document metadata
            document_metadata.append((doc_id, document.title, doc_length))

            # Batch insert metadata if threshold reached
            if len(document_metadata) >= 1000:
                self.batch_insert_document_metadata(document_metadata)
                document_metadata = []

            total_tokens += doc_length

            # Progress callback handling
            if progress_callback:
                progress_fraction = 0.50 * (i + 1) / num_docs
                progress_callback(progress_fraction)

        # Insert any remaining metadata after the loop
        if document_metadata:
            self.batch_insert_document_metadata(document_metadata)

        # Update the corpus stats with the total number of tokens
        self.db_cursor.execute('REPLACE INTO corpus_stats (stat_name, value) VALUES ("total_tokens", ?)', (total_tokens,))
        self.db_conn.commit()

        self.memory_index()
        self.merge_files(lambda fraction: progress_callback(0.50 + 0.50 * fraction), self.uniq_terms)

        doc_squares_sum = {}
        for doc_id, terms in doc_term_freq.items():
            squares_sum = sum((1 + math.log(tf))**2 for tf in terms.values() if tf > 0)
            doc_squares_sum[doc_id] = squares_sum

        euclidean_lengths = {}
        for doc_id, squares_sum in doc_squares_sum.items():
            euclidean_length = math.sqrt(squares_sum)
            euclidean_lengths[doc_id] = euclidean_length

        os.makedirs(WEIGHTS_DIR, exist_ok=True)
        doc_weights_file_path = os.path.join(WEIGHTS_DIR, "docWeights.bin")
        self.write_doc_weights(euclidean_lengths, doc_weights_file_path)

        print("SPIMI indexing completed.")

    def memory_index(self):
        """Sorts the in-memory index and writes it to disk."""
        file_path = os.path.join(BUCKET_DIR, f"bucket_{self.file_counter}.bin")
        
        with open(file_path, "wb") as postings_file:
            sorted_terms = self.p_i_index.getVocabulary()
            for term in sorted_terms:
                if term:
                    self.uniq_terms += 1
                    postings = self.p_i_index.getPostings(term)
                    encoded_postings = self._encode_postings(term, postings)
                    # Format <term length><term><df><doc_id><tftd><position>
                    postings_file.write(encoded_postings)
        
        self.db_conn.commit()  
        self.file_counter += 1
        self.p_i_index.clear()

    def _encode_postings(self, term, postings_list):
        """Encodes the postings list using gap encoding."""
        # Encode the term length as an integer (4 bytes)
        term_bytes = b''.join([struct.pack('B', ord(character)) for character in term])
        term_length = len(term_bytes)

        # Encode the term length as an integer (4 bytes)
        postings_data = struct.pack('I', term_length)

        # Append the term
        postings_data += term_bytes

        # Encode the document frequency as an integer (4 bytes)
        dtf = struct.pack('I', len(postings_list))
        postings_data += dtf
        last_doc_id = 0

        for posting in postings_list:
            # Check if posting is a dict or an object and access doc_id and positions
            if isinstance(posting, dict):
                doc_id = posting['doc_id']
                positions = posting['positions']
            else:  # assuming it's an object
                doc_id = posting.doc_id
                positions = posting.positions

            # Encode the document id as an integer (4 bytes)
            doc_gap = doc_id - last_doc_id
            postings_data += struct.pack('I', doc_gap)
            last_doc_id = doc_id

            # Encode the term frequency in the document as an integer (4 bytes)
            tftd = len(positions)
            postings_data += struct.pack('I', tftd)

            last_position = 0
            for position in positions:
                # Encode the position as an integer (4 bytes)
                position_gap = position - last_position
                postings_data += struct.pack('I', position_gap)
                last_position = position

        return postings_data

    def merge_files(self, progress_callback=None, total_terms=0):
        print("Merging Files...")
        
        # Open read streams for each intermediate file
        file_streams = [open(os.path.join(BUCKET_DIR, f"bucket_{i}.bin"), "rb") for i in range(self.file_counter)]
        
        # Track whether a stream is exhausted
        stream_exhausted = [False] * len(file_streams)

        # Open write stream for final merged file
        merged_file_path = os.path.join(POSTINGS_DIR, "postings.bin")
        with open(merged_file_path, "wb") as merged_file:

            # Initialize priority queue
            pq = []
            for index, file_stream in enumerate(file_streams):
                first_posting = self._read_postings_data(file_stream)
                if first_posting:
                    heapq.heappush(pq, Posting(first_posting[0][0], index, first_posting))

            # Initialize buffer for batch database updates
            db_update_buffer = []
            db_update_threshold = 1000  

            # Merge process
            processed_terms = 0
            while pq:
                current_posting = heapq.heappop(pq)
                current_term = current_posting.term
                L = [current_posting.postings_data]

                # While the next term is the same as the current one
                while pq and pq[0].term == current_term:
                    same_term_posting = heapq.heappop(pq)
                    L.append(same_term_posting.postings_data)

                    # Get next posting from the same file
                    if not stream_exhausted[same_term_posting.file_index]:
                        next_posting = self._read_postings_data(file_streams[same_term_posting.file_index])
                        if next_posting:
                            heapq.heappush(pq, Posting(next_posting[0][0], same_term_posting.file_index, next_posting))
                        else:
                            stream_exhausted[same_term_posting.file_index] = True

                # Merge L and write to file
                merged_postings = self.merge_postings(L)
                formatted_postings = [{'doc_id': posting[0], 'positions': posting[2]} for posting in merged_postings]

                # Record the start position
                start_position = merged_file.tell()
                db_update_buffer.append((current_term, start_position))

                # Write to file
                encoded_data = self._encode_postings(current_term, formatted_postings)
                merged_file.write(encoded_data)

                # Push the next posting from the file we just processed to the priority queue
                if not pq or pq[0].file_index != current_posting.file_index:
                    if not stream_exhausted[current_posting.file_index]:
                        next_posting = self._read_postings_data(file_streams[current_posting.file_index])
                        if next_posting:
                            heapq.heappush(pq, Posting(next_posting[0][0], current_posting.file_index, next_posting))
                        else:
                            stream_exhausted[current_posting.file_index] = True

                processed_terms += 1
                if progress_callback and total_terms:
                    progress_fraction = processed_terms / total_terms
                    progress_callback(progress_fraction)

                # Batch update to the database
                if len(db_update_buffer) >= db_update_threshold:
                    self.db_cursor.executemany('REPLACE INTO term_positions (term, position) VALUES (?, ?)', db_update_buffer)
                    db_update_buffer = []

            # Final database update for remaining items
            if db_update_buffer:
                self.db_cursor.executemany('REPLACE INTO term_positions (term, position) VALUES (?, ?)', db_update_buffer)
            self.db_conn.commit()

            if progress_callback:
                progress_callback(1.0)

            # Close all streams
            for file_stream in file_streams:
                file_stream.close()

        print("Merging completed.")


    @staticmethod
    def merge_postings(postings_lists):
        merged_postings = {}
        # Combine postings for the same term from different blocks.
        for postings in postings_lists:
            for _, doc_id, tftd, positions in postings:
                if doc_id in merged_postings:
                    # Merge positions for the same doc_id.
                    merged_postings[doc_id]['positions'].extend(positions)
                else:
                    # Add new doc_id with its positions.
                    merged_postings[doc_id] = {'positions': positions, 'tftd': tftd}

        # Sort the combined postings by doc_id and sort the positions list for each posting.
        sorted_postings = []
        for doc_id, data in sorted(merged_postings.items()):
            sorted_positions = sorted(data['positions'])
            sorted_postings.append((doc_id, data['tftd'], sorted_positions))

        return sorted_postings

    def _read_postings_data(self, stream):
        """Reads the next postings data from the specified stream."""
        postings = []
        last_doc_id = 0

        # Read the term length
        term_length_data = stream.read(4)

        if not term_length_data:
            return None

        term_length = struct.unpack('I', term_length_data)[0]

        # Read and decode the term
        term_bytes = stream.read(term_length)
        term = ''.join([chr(struct.unpack('B', bytes([b]))[0]) for b in term_bytes])

        # Read the document frequency
        dtf_data = stream.read(4)
        if not dtf_data:  
            return None

        dtf = struct.unpack('I', dtf_data)[0]

        for _ in range(dtf):
            # Read the document id
            doc_gap_data = stream.read(4)
            if not doc_gap_data: 
                break  
            doc_gap = struct.unpack('I', doc_gap_data)[0]
            doc_id = last_doc_id + doc_gap
            last_doc_id = doc_id

            # Read the term frequency in the document
            tftd_data = stream.read(4)
            if not tftd_data:  
                break  
            tftd = struct.unpack('I', tftd_data)[0]

            last_position = 0
            position_data = []
            for _ in range(tftd):
                # Read the positions
                pos_gap_data = stream.read(4)
                if not pos_gap_data:
                    break  
                pos_gap = struct.unpack('I', pos_gap_data)[0]
                position = last_position + pos_gap
                position_data.append(position)
                last_position = position

            postings.append((term, doc_id, tftd, position_data))

        return postings

    def memory_limit(self, total_memory):
        MEMORY_LIMIT = 15000000 # 15 MB
        return total_memory > MEMORY_LIMIT

    def write_doc_weights(self, doc_lengths: dict[int, float], doc_weights_file_path: str):
        """Writes the document weights (Euclidean lengths) to the specified file."""
        with open(doc_weights_file_path, 'wb') as doc_weights_file:
            for doc_id in sorted(doc_lengths.keys()):
                L_d = doc_lengths[doc_id]
                doc_weights_file.write(struct.pack('d', L_d))
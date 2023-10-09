from engine.documents import DocumentCorpus, DirectoryCorpus, TextFileDocument, JsonDocument
from engine.text import BasicTokenProcessor, EnglishTokenStream
from engine.indexing import Index, PositionalInvertedIndex
from engine.querying import BooleanQueryParser
from tkinter import filedialog, Label, ttk
from pathlib import Path
from io import StringIO
from datetime import timedelta
from .decorators import threaded
import time
import threading
import re
import traceback
import queue

class CorpusManager:
    def __init__(self):
        self.corpus = None
        self.p_i_index = PositionalInvertedIndex()
        self.processor = BasicTokenProcessor()

    def load_corpus(self, folder_selected):
        extension_factories = {
            '.txt': TextFileDocument.load_from,
            '.json': JsonDocument.load_from
        }
        self.corpus = DirectoryCorpus.load_directory(folder_selected, extension_factories)
        return self.corpus

    def index_corpus(self, progress_callback=None):
        for i, doc_path in enumerate(self.corpus):
            tokens = EnglishTokenStream(doc_path.get_content())
            position = 0
            for token in tokens:
                position += 1
                types = self.processor.process_token(token)
                for type in types:
                    term = self.processor.normalize_type(type)
                    self.p_i_index.addTerm(term, doc_path.id, position)

            if progress_callback:
                progress_callback(i)

        return self.p_i_index.getVocabulary()

class UIManager:
    def __init__(self, master, view, corpus_manager, search_manager):
        self.master = master
        self.view = view
        self.corpus_manager = corpus_manager
        self.search_manager = search_manager
        self.total_documents = 0

    @threaded
    def load_corpus_ui(self):
        """Load and tokenize a corpus folder that user selects."""
        folder_selected = filedialog.askdirectory()
        if not folder_selected:
            self.show_warning("Please choose a valid directory.")
            return

        self.corpus_manager.load_corpus(folder_selected)

        # Calculate number of documents
        self.total_documents = sum(1 for _ in self.corpus_manager.corpus)

        self.progress = ttk.Progressbar(self.view.pages["HomePage"].centered_frame, 
                                        orient='horizontal', 
                                        length=300, 
                                        mode='determinate', 
                                        maximum=self.total_documents) 

        self.progress_info_label = Label(self.view.pages["HomePage"].centered_frame, 
                                         text="Progress: 0%", 
                                         bg='#ffffff', 
                                         font=("Arial", 10))

        self.progress.grid(row=3, column=0, columnspan=3, pady=5, padx=50)
        self.progress_info_label.grid(row=4, column=0, columnspan=3, pady=5)
        
        # Start the indexing
        self.corpus_manager.index_corpus(self.update_progress_ui)

        # After indexing
        self.progress.grid_forget()
        self.progress_info_label.grid_forget()

    def update_progress_ui(self, current_document_index):
        """Update the progress UI based on the indexed documents."""
        percentage_complete = (current_document_index / self.total_documents) * 100
        self.progress['value'] = current_document_index
        self.progress_info_label.config(text=f"Progress: {percentage_complete:.1f}%")
        self.view.master.update_idletasks()  

    @threaded
    def perform_search_ui(self):
        # UI interactions for the search operation run in a new thread
        self.search_manager.perform_search()

    def show_warning(self, message):
        self.view.pages["HomePage"].home_warning_label.config(text=message)


class SearchManager:
    def __init__(self, corpus_manager, view, search_entry, results_search_entry, home_warning_label, canvas):
        self.corpus_manager = corpus_manager
        self.processor = BasicTokenProcessor()
        self.view = view
        self.search_entry = search_entry
        self.results_search_entry = results_search_entry
        self.home_warning_label = home_warning_label
        self.canvas = canvas

    def perform_search(self):
        if not self.corpus_manager.corpus or not self.corpus_manager.p_i_index:
            self.home_warning_label.config(text="Please load a corpus first.")
            return

        if self.view.pages["HomePage"].winfo_ismapped():
            raw_query = self.view.pages["HomePage"].search_entry.get()
        else:
            raw_query = self.view.pages["ResultsPage"].results_search_entry.get()

        if not raw_query:
            self.home_warning_label.config(text="Please enter a search query.")
            return

        if not self.view.pages["ResultsPage"].winfo_ismapped():
            self.view.show_page("ResultsPage")

        self.view.pages["ResultsPage"].clear_results()

        # Identify terms and operators separately
        terms = re.split(r'([+])', raw_query)
        token_processor = BasicTokenProcessor()

        # Process terms and construct the normalized query
        processed_query_parts = [
            term if term == '+' else ' '.join(
                token_processor.normalize_type(token)
                for t in EnglishTokenStream(StringIO(term.strip()))
                for token in token_processor.process_token(t)
            ) for term in terms
        ]
        normalized_query = ''.join(processed_query_parts)

        try:
            self.view.pages["ResultsPage"].show_results_page(raw_query)

            parsed_query = BooleanQueryParser.parse_query(normalized_query)
            if not parsed_query:
                self.home_warning_label.config(text="Invalid Query. Please enter a valid search query.")
                return

            postings = parsed_query.getPostings(self.corpus_manager.p_i_index)
            found_docs = {posting.doc_id for posting in postings}

            if not found_docs: 
                self.view.pages["ResultsPage"].display_no_results_warning()
                return

            for doc_id in found_docs:
                doc = next((d for d in self.corpus_manager.corpus if d.id == doc_id), None)

                if doc:
                    # Extract a sentence containing the parsed query and display the search result
                    content_sentence = self.find_sentence_containing_query(''.join(doc.get_content()), normalized_query)
                    self.view.pages["ResultsPage"].add_search_result_to_window(doc.id, doc.title, content_sentence)

            self.canvas.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        except Exception as e:
            self.view.pages["ResultsPage"].display_no_results_warning(str(e))
            print("Error during search:", str(e))
            traceback.print_exc()

    def find_sentence_containing_query(self, document_content, query):
        sentences = re.split(r'(?<=[.!?])\s+', document_content)
        query_tokens = set(
            self.processor.normalize_type(t) 
            for word in query.split() 
            for t in self.processor.process_token(word)
        )

        for i, sentence in enumerate(sentences):
            sentence_tokens = set(
                self.processor.normalize_type(t)
                for word in sentence.split() 
                for t in self.processor.process_token(word)
            )
            if query_tokens & sentence_tokens:
                return ' '.join((
                    sentences[i-1] if i-1 >= 0 else "",
                    sentence,
                    sentences[i+1] if i+1 < len(sentences) else ""
                )).strip()
        return None
    

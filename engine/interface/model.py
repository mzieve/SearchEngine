from engine.documents import DocumentCorpus, DirectoryCorpus, TextFileDocument, JsonDocument, XMLDocument
from engine.text import BasicTokenProcessor, SpanishTokenProcessor, EnglishTokenStream, SpanishTokenStream, Preprocessing
from engine.indexing import Index, PositionalInvertedIndex
from engine.querying import BooleanQueryParser
from tkinter import filedialog, Label, ttk
from pathlib import Path
from io import StringIO, TextIOWrapper
from .decorators import threaded, threaded_value
import time
import re
import traceback
import queue
import io
import builtins
import config

class CorpusManager:
    def __init__(self):
        self.corpus = None
        self.preprocess = Preprocessing()

    def load_corpus(self, folder_selected):
        extension_factories = {
            '.txt': TextFileDocument.load_from,
            '.json': JsonDocument.load_from,
            '.xml': XMLDocument.load_from
        }
        self.corpus = DirectoryCorpus.load_directory(folder_selected, extension_factories)
        return self.corpus

    def index_corpus(self, progress_callback=None):
        # Detect the language using the first document in the corpus
        first_doc_content = self.corpus[0].get_content()
        if isinstance(first_doc_content, io.TextIOWrapper):
            lang_content = first_doc_content.read()
        else:
            lang_content = ' '.join(first_doc_content)
        
        language = self.preprocess.detect_language(lang_content)
        config.LANGUAGE = language

        return self.preprocess.dic_process_position(self.corpus, progress_callback)

class SearchManager:
    def __init__(self, corpus_manager, preprocess, view, search_entry, results_search_entry, home_warning_label, canvas):
        self.corpus_manager = corpus_manager
        self.view = view
        self.search_entry = search_entry
        self.results_search_entry = results_search_entry
        self.home_warning_label = home_warning_label
        self.canvas = canvas
        self.preprocess = preprocess

    def perform_search(self):
        if not self._corpus_ready():
            return

        raw_query = self._get_raw_query()

        if not raw_query: 
            self.home_warning_label.config(text="Please enter a search query.")
            return

        self.view.pages["ResultsPage"].show_results_page(raw_query)
        self._prepare_results_page()

        try:
            query = BooleanQueryParser.parse_query(raw_query, self.preprocess)
            postings = self._get_postings(query)

            if not postings:
                self.view.pages["ResultsPage"].display_no_results_warning()
                return

            self._display_search_results(postings, query)

        except SpecificException as e: 
            self._handle_search_error(e)

    def _corpus_ready(self):
        if not self.corpus_manager.corpus:
            self.home_warning_label.config(text="Please load a corpus first.")
            return False
        return True

    def _get_raw_query(self):
        if self.view.pages["HomePage"].winfo_ismapped():
            return self.view.pages["HomePage"].search_entry.get()
        return self.view.pages["ResultsPage"].results_search_entry.get()

    def _prepare_results_page(self):
        if not self.view.pages["ResultsPage"].winfo_ismapped():
            self.view.show_page("ResultsPage")
        self.view.pages["ResultsPage"].clear_results()


    def _get_postings(self, query):
        if not query:
            self.home_warning_label.config(text="Invalid Query. Please enter a valid search query.")
            return []

        postings = query.getPostings(self.preprocess.p_i_index)
        return postings

    def _display_search_results(self, postings, query):
        for posting in postings:
            doc = next((d for d in self.corpus_manager.corpus if d.id == posting.doc_id), None)
            if doc:
                self.view.pages["ResultsPage"].add_search_result_to_window(doc.id, doc.title, None)
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _handle_search_error(self, exception):
        self.view.pages["ResultsPage"].display_no_results_warning(str(exception))
        print("Error during search:", str(exception))
        traceback.print_exc()

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

        self.progress.grid(row=3, column=0, columnspan=3, pady=0, padx=50)
        self.progress_info_label.grid(row=4, column=0, columnspan=3, pady=0)
        
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
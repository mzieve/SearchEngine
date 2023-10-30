from engine.documents import (
    DocumentCorpus,
    DirectoryCorpus,
    TextFileDocument,
    JsonDocument,
    XMLDocument,
)
from engine.text import (
    BasicTokenProcessor,
    SpanishTokenProcessor,
    EnglishTokenStream,
    SpanishTokenStream,
    Preprocessing,
)
from engine.indexing import Index, PositionalInvertedIndex
from engine.querying import BooleanQueryParser
from tkinter import filedialog, Label, ttk
import customtkinter # type: ignore
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
            ".txt": TextFileDocument.load_from,
            ".json": JsonDocument.load_from,
            ".xml": XMLDocument.load_from,
        }
        self.corpus = DirectoryCorpus.load_directory(
            folder_selected, extension_factories
        )
        return self.corpus

    def index_corpus(self, progress_callback=None):
        # Detect the language using the first document in the corpus
        first_doc_content = self.corpus[0].get_content()
        if isinstance(first_doc_content, io.TextIOWrapper):
            lang_content = first_doc_content.read()
        else:
            lang_content = " ".join(first_doc_content)

        language = self.preprocess.detect_language(lang_content)
        config.LANGUAGE = language

        return self.preprocess.dic_process_position(self.corpus, progress_callback)


class SearchManager:
    def __init__(
        self,
        corpus_manager,
        preprocess,
        view,
        search_entry,
        results_search_entry,
        home_warning_label,
        canvas,
    ):
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
            self.home_warning_label.configure(text="Please enter a search query.")
            return

        self.view.pages["ResultsPage"].show_results_page(raw_query)
        self._prepare_results_page()

        try:
            query = BooleanQueryParser.parse_query(raw_query, self.preprocess)
            postings = self._get_postings(query)

            if not postings:
                self.view.pages["ResultsPage"].display_no_results_warning(raw_query)
                return

            self._display_search_results(postings)

        except Exception as e:
            self._handle_search_error(e)

    def _corpus_ready(self):
        if not self.corpus_manager.corpus:
            self.home_warning_label.configure(text="Please load a corpus first.")
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
            self.home_warning_label.configure(
                text="Invalid Query. Please enter a valid search query."
            )
            return []

        postings = query.getPostings(self.preprocess.p_i_index)
        return postings

    def _display_search_results(self, postings):
        results = len(postings)
        self.view.pages["ResultsPage"].results_frame.update_results_count(results)

        data_items = [
            f"Document ID# {posting.doc_id} - {next((d for d in self.corpus_manager.corpus if d.id == posting.doc_id), None).title}"
            for posting in postings
        ]

        self.view.pages["ResultsPage"].results_frame.data_items = data_items
        self.view.pages["ResultsPage"].results_frame.load_initial_widgets()

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

        # Create the progress frame
        self.progress_frame = customtkinter.CTkFrame(self.view.pages["HomePage"].centered_frame, fg_color="#2b2b2b")
        self.progress_frame.grid(row=4, column=0, pady=0)

        self.progress_frame.rowconfigure(0, weight=0, minsize=30)
        self.progress_frame.rowconfigure(1, weight=1, minsize=30)

        self.progress = customtkinter.CTkProgressBar(
            self.progress_frame,
            mode="determinate",
            width=500,
            height=10,
            progress_color="#7236bf"
        )
        self.progress.set(0)
        self.progress.grid(row=0, column=0, pady=(0,15))

        self.progress_info_label = customtkinter.CTkLabel(
            self.progress_frame,
            text="Progress: 0%",
            font=("Arial", 14),
        )
        self.progress_info_label.grid(row=1, column=0, pady=0)

        self.corpus_manager.load_corpus(folder_selected)

        # Calculate number of documents
        self.total_documents = sum(1 for _ in self.corpus_manager.corpus)

        # Start the indexing
        self.corpus_manager.index_corpus(self.update_progress_ui)

        # After indexing
        self.progress.grid_forget()
        self.progress_info_label.grid_forget()
        self.progress_frame.grid_forget()

    def update_progress_ui(self, current_document_index):
       """Schedule the progress UI update."""
       self.master.after(0, self._update_progress_ui_on_main_thread, current_document_index)

    def _update_progress_ui_on_main_thread(self, current_document_index):
        """Update the progress UI based on the indexed documents."""
        progress_fraction = current_document_index / self.total_documents
        percentage_complete = progress_fraction * 100

        self.progress.set(progress_fraction)
        self.progress_info_label.configure(text=f"Progress: {percentage_complete:.1f}%")

    def perform_search_ui(self):
        # UI interactions for the search operation run in a new thread
        self.search_manager.perform_search()

    def show_warning(self, message):
        self.view.pages["HomePage"].home_warning_label.configure(text=message)

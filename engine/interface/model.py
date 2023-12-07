from engine.indexing import (
    Index,
    PositionalInvertedIndex,
    DiskIndexWriter,
    DiskPositionalIndex,
)
from config import (
    DB_PATH,
    POSTINGS_FILE_PATH,
    DOC_WEIGHTS_FILE_PATH,
    DATA_DIR,
    SPIMI_DIR,
)
from engine.querying import BooleanQueryParser, PhraseLiteral
from tkinter import filedialog, Label, ttk
import customtkinter  # type: ignore
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
import os
import json
import sqlite3
from engine.text import (
    BasicTokenProcessor,
    SpanishTokenProcessor,
    EnglishTokenStream,
    SpanishTokenStream,
    Preprocessing,
)
from engine.documents import (
    DocumentCorpus,
    DirectoryCorpus,
    TextFileDocument,
    JsonDocument,
    XMLDocument,
    SPIMI,
)


class CorpusManager:
    def __init__(self, search_manager):
        self.corpus = None
        self.preprocess = Preprocessing()
        self.search_manager = search_manager

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
        """
        first_doc_content = self.corpus[0].get_content()
        lang_content = (
            first_doc_content.read()
            if isinstance(first_doc_content, io.TextIOWrapper)
            else " ".join(first_doc_content)
        )
        language = self.preprocess.detect_language(lang_content)
        config.LANGUAGE = language

        # Write language to file
        language_file_path = os.path.join(DATA_DIR, "language.json")
        with open(language_file_path, "w") as language_file:
            json.dump({"language": language}, language_file)
        """

        spimi = SPIMI(SPIMI_DIR, self.corpus)
        spimi.spimi_index(progress_callback=progress_callback)

        if self.search_manager:
            self.search_manager.initialize_disk_index()

    def load_language_setting(self):
        language_file_path = os.path.join(DATA_DIR, "language.json")
        if os.path.exists(language_file_path):
            with open(language_file_path, "r") as language_file:
                language_data = json.load(language_file)
                config.LANGUAGE = language_data.get("language")


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
        self.disk_index = None

    def initialize_disk_index(self):
        if self.is_indexed():
            self.disk_index = self.load_disk_index()

    def is_indexed(self):
        """Check if the index files exist."""
        db_exists = os.path.exists(DB_PATH)
        postings_exists = os.path.exists(POSTINGS_FILE_PATH)
        return db_exists and postings_exists

    def load_disk_index(self):
        """Load the disk index if it exists."""
        try:
            return DiskPositionalIndex(DB_PATH, POSTINGS_FILE_PATH)
        except Exception as e:
            if self.home_warning_label:
                self.home_warning_label.configure(text=f"Error loading disk index: {e}")
            else:
                print(f"Error loading disk index: {e}")
            return None

    def perform_search(self):
        self.corpus_manager.load_language_setting()

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
        if self.disk_index is None or not os.path.exists(DB_PATH):
            self.home_warning_label.configure(text="Please index the corpus first.")
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

    def _is_phrase_query(self, query_component):
        """
        Recursively checks if any part of the query is a PhraseLiteral.
        """
        if isinstance(query_component, PhraseLiteral):
            return True
        elif hasattr(query_component, "components"):
            return any(
                self._is_phrase_query(comp) for comp in query_component.components
            )
        return False

    def _get_postings(self, query):
        if not query:
            self.home_warning_label.configure(
                text="Invalid Query. Please enter a valid search query."
            )
            return []

        # Set the flag in DiskPositionalIndex based on the type of query
        self.disk_index.set_phrase_query(self._is_phrase_query(query))

        # Fetch postings from the DiskPositionalIndex
        postings = query.getPostings(self.disk_index)

        # Reset the flag after fetching postings
        self.disk_index.set_phrase_query(False)

        return postings

    def _display_search_results(self, postings):
        results = len(postings)
        self.view.pages["ResultsPage"].results_frame.update_results_count(results)

        data_items = [
            f"Document ID# {posting.doc_id} - {self.get_document_title(posting.doc_id)}"
            for posting in postings
        ]
        self.view.pages["ResultsPage"].results_frame.data_items = data_items
        self.view.pages["ResultsPage"].results_frame.load_initial_widgets()

    def get_document_title(self, doc_id):
        """Retrieve the title of a document based on its document ID."""
        if self.disk_index:
            try:
                self.disk_index.db_cursor.execute(
                    "SELECT title FROM document_metadata WHERE doc_id = ?", (doc_id,)
                )
                result = self.disk_index.db_cursor.fetchone()
                if result:
                    return result[0]  # Returns the title
                else:
                    return "Title not found"
            except Exception as e:
                print(f"Error retrieving document title: {e}")
                return "Error retrieving title"
        else:
            return "Index not loaded"

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
        self.progress_frame = customtkinter.CTkFrame(
            self.view.pages["HomePage"].centered_frame, fg_color="#2b2b2b"
        )
        self.progress_frame.grid(row=4, column=0, pady=0)

        self.progress_frame.rowconfigure(0, weight=0, minsize=30)
        self.progress_frame.rowconfigure(1, weight=1, minsize=30)

        self.progress = customtkinter.CTkProgressBar(
            self.progress_frame,
            mode="determinate",
            width=500,
            height=10,
            progress_color="#7236bf",
        )
        self.progress.set(0)
        self.progress.grid(row=0, column=0, pady=(0, 15))

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
        self.corpus_manager.index_corpus(progress_callback=self.update_progress_ui)

        # After indexing
        self.progress.grid_forget()
        self.progress_info_label.grid_forget()
        self.progress_frame.grid_forget()

    def update_progress_ui(self, current_document_index, total_documents):
        """Update the progress UI based on the indexed documents."""
        progress_fraction = (current_document_index + 1) / total_documents
        self.master.after(0, self._update_progress_ui_on_main_thread, progress_fraction)

    def _update_progress_ui_on_main_thread(self, progress_fraction):
        """Update the progress UI on the main thread."""
        percentage_complete = progress_fraction * 100
        self.progress.set(progress_fraction)
        self.progress_info_label.configure(text=f"Progress: {percentage_complete:.1f}%")

    def perform_search_ui(self):
        # UI interactions for the search operation run in a new thread
        self.search_manager.perform_search()

    def show_warning(self, message):
        self.view.pages["HomePage"].home_warning_label.configure(text=message)

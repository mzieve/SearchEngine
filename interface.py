import sys
sys.path.append("")
# Adds higher directory to python modules path.

from pathlib import Path
from documents import DocumentCorpus, DirectoryCorpus, TextFileDocument, JsonDocument
from text import BasicTokenProcessor, EnglishTokenStream
from indexing import Index, PositionalInvertedIndex
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, Label
import tkinter.font as font
import os
import time
import threading

class SearchEngineGUI:
    def __init__(self, master):
        """Initialize the GUI components."""
        self.master = master
        self.master.title("Querlo")
        self.master.configure(bg='#ffffff')
        self._center_window(1000, 800)
        self._add_logo()
        self._add_search_entry()
        self._add_search_button()
        self.corpus = None
        self.p_i_index = PositionalInvertedIndex()
        self.processor = BasicTokenProcessor()

    def _center_window(self, width, height):
        """Center the application window on the screen."""
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (width / 2))
        y_coordinate = int((screen_height / 2) - (height / 2))
        self.master.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")

    def _add_logo(self):
        """Add the application logo to the GUI."""
        logo_frame = tk.Frame(self.master)
        logo_frame.pack(pady=(230, 5))
        logo_label = tk.Label(logo_frame, text="Querlo", font=("Arial", 62), fg="#ffffff", bg="#ff5733")
        logo_label.pack()

    def _add_search_entry(self):
        """Add the search entry box to the GUI."""
        self.search_entry = tk.Entry(
            self.master, width=90, borderwidth=25, bg='#ffffff',
            insertbackground='black', bd=1, relief='flat', fg="#000000",
            highlightthickness=2, highlightbackground="light grey"
        )
        self.search_entry.pack(ipady=8, pady=20)


    def _add_search_button(self):
        """Add the search button to the GUI."""
        button_frame = tk.Frame(self.master, bg='#ffffff')  
        button_frame.pack(pady=10)

        # Querlo Search Button
        search_btn = tk.Button(
            button_frame, text="Querlo Search", command=self.perform_search,
            bg="#faf5f5", fg="black", height=2, width=15, font=("Arial", 10), relief='flat',
            highlightthickness=0, highlightbackground="#ffffff", bd=0
        )
        search_btn.grid(row=0, column=0, padx=10)

        # Load Corpus Button
        load_corpus_btn = tk.Button(
            button_frame, text="Load Corpus", command=self.load_corpus,
            bg="#faf5f5", fg="black", height=2, width=15, font=("Arial", 10), relief='flat',
            highlightthickness=0, highlightbackground="#ffffff", bd=0
        )
        load_corpus_btn.grid(row=0, column=1, padx=10)

        # Message label for displaying warnings, initially empty
        self.warning_label = tk.Label(button_frame, text="", fg="red", bg='#ffffff', font=("Arial", 10))
        self.warning_label.grid(row=1, columnspan=2, pady=15)

    def load_corpus(self):
        """Threading needed to prevent GUI freezing"""
        threading.Thread(target=self._load_corpus_thread).start()

    def _load_corpus_thread(self):
        """Load tokenize a corpus folder that user selects"""
        folder_selected = filedialog.askdirectory()

        if folder_selected:
            corpus_path = Path(folder_selected)
            extension_factories = {
                '.txt': TextFileDocument.load_from,
                '.json': JsonDocument.load_from
            }
            load_start_time = time.time()
            self.corpus = DirectoryCorpus.load_directory(corpus_path, extension_factories)
            load_end_time = time.time()
            load_dir_time = load_end_time-load_start_time
            load_dir_mins = (load_dir_time // 60)
            load_dir_secs = (load_dir_time % 60)
            print("Time to load directory into corpus: {} mins, {} seconds".format(load_dir_mins, load_dir_secs))

            num_documents = sum(1 for _ in self.corpus)
            total_operations = 3 * num_documents

            # Progress bar
            progress = ttk.Progressbar(self.master, orient='horizontal', length=300, mode='determinate')
            progress['maximum'] = total_operations
            progress.pack()

            progress_label = Label(self.master, text="Progress: 0%", bg='#ffffff', font=("Arial", 10))
            progress_label.pack()

            self.master.update_idletasks()

            index_start_time = time.time()

            for i, doc_path in enumerate(self.corpus):
                # Elapsed time to build index
                elapsed_time = time.time() - index_start_time
                avg_time_per_doc = elapsed_time / (i + 1)
                remaining_docs = num_documents - i - 1
                estimated_time_remaining = avg_time_per_doc * remaining_docs
                
                # Calculate progress percentage
                percentage_complete = (progress['value'] / total_operations) * 100
                
                # Mintues to seconds
                if estimated_time_remaining > 60:
                    estimated_minutes = int(estimated_time_remaining // 60)
                    estimated_seconds = int(estimated_time_remaining % 60)
                    progress_label.config(text=f"Progress: {percentage_complete:.1f}%. Estimated time: {estimated_minutes}m {estimated_seconds}s")
                else:
                    progress_label.config(text=f"Progress: {percentage_complete:.1f}%. Estimated time: {int(estimated_time_remaining)}s")

                #self.corpus.append(doc_path)
                progress['value'] += 1
                self.master.update_idletasks()

                # Process tokens
                tokens = EnglishTokenStream(doc_path.get_content())
                position = 0
                for token in tokens:
                    position += 1
                    types = self.processor.process_token(token)
                    # Normalize each type into a term, then add the term and its docID and position into the index.
                    for type in types:
                        term = self.processor.normalize_type(type)
                        self.p_i_index.addTerm(term, doc_path.id, position)

                progress['value'] += 2
                self.master.update_idletasks()

            progress.destroy()
            progress_label.destroy()
            index_end_time = time.time()
            index_corpus_time = index_end_time - index_start_time
            index_corpus_mins = (index_corpus_time // 60)
            index_corpus_secs = (index_corpus_time % 60)
            print("Time to index corpus: {} mins, {} seconds".format(index_corpus_mins, index_corpus_secs))
            total_secs = load_dir_secs + index_corpus_secs
            total_mins = load_dir_mins + index_corpus_mins
            if (total_secs > 60):
                extra_mins = total_secs // 60
                total_secs = total_secs % 60
                total_mins += extra_mins
            print("Total time to load corpus: {} mins, {} seconds".format(total_mins, total_secs))
            print("Corpus loaded! Ready to search.")
            vocabulary = self.p_i_index.getVocabulary()
            vocab_set = set(vocabulary)

            return vocab_set

    def perform_search(self):
        """Perform a search query based on the user's input in the search box."""
        query = self.search_entry.get()
        print("Searching for the term '{}'".format(query))
        if self.corpus:
            self.warning_label.config(text="")  # Clear any previous warnings
            query_types = self.processor.process_token(query)
            for query_type in query_types:
                query_term = self.processor.normalize_type(query_type)
                for p in self.p_i_index.getPostings(query_term):
                    doc = self.corpus.get_document(p.doc_id)
                    print("Doc ID {}. \"{}\" at positions {}". format(p.doc_id, doc.title, p.positions))
        else:
            # Update warning label if no corpus is loaded
            self.warning_label.config(text="Please load a corpus to perform a search.")
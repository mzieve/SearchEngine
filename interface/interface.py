from pathlib import Path
from documents import DirectoryCorpus, TextFileDocument, JsonDocument
from text import BasicTokenProcessor, EnglishTokenStream
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

            vocabulary = set()
            processor = BasicTokenProcessor()
            num_documents = sum(1 for _ in DirectoryCorpus.load_directory(corpus_path, extension_factories))
            total_operations = 3 * num_documents

            # Progress bar
            progress = ttk.Progressbar(self.master, orient='horizontal', length=300, mode='determinate')
            progress['maximum'] = total_operations
            progress.pack()

            progress_label = Label(self.master, text="Progress: 0%", bg='#ffffff', font=("Arial", 10))
            progress_label.pack()

            self.master.update_idletasks()
            self.corpus = []

            start_time = time.time()

            for i, doc_path in enumerate(DirectoryCorpus.load_directory(corpus_path, extension_factories)):
                # Elapsed time to load
                elapsed_time = time.time() - start_time
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

                self.corpus.append(doc_path)
                progress['value'] += 1
                self.master.update_idletasks()

                # Process tokens
                tokens = EnglishTokenStream(doc_path.get_content())
                processed_tokens = [processor.process_token(token) for token in tokens]

                # Flatten the processed tokens list
                flat_processed_tokens = [token for sublist in processed_tokens for token in sublist]

                # Normalize the tokens
                normalized_tokens = [processor.normalize_type(token) for token in flat_processed_tokens]
                vocabulary.update(normalized_tokens)

                progress['value'] += 2
                self.master.update_idletasks()

            progress.destroy()
            progress_label.destroy()
            
            return vocabulary

    def perform_search(self):
        """Perform a search query based on the user's input in the search box."""
        query = self.search_entry.get()
        if self.corpus:
            self.warning_label.config(text="")  # Clear any previous warnings
            # TODO: Implement actual search logic here.
            # The following is just a placeholder.
            for doc in self.corpus:
                if query.lower() in doc.title.lower():
                    print(f"Document ID: {doc.id}, Title: {doc.title}")
        else:
            # Update warning label if no corpus is loaded
            self.warning_label.config(text="Please load a corpus to perform a search.")
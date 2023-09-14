from pathlib import Path
from documents import DirectoryCorpus, TextFileDocument, JsonDocument
import tkinter as tk
from tkinter import filedialog
import tkinter.font as font
import os

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
            self.master, width=90, borderwidth=15, bg='white',
            insertbackground='black', bd=0, relief='flat',
            highlightthickness=1, highlightbackground="light gray", insertwidth=1
        )
        self.search_entry.pack(ipady=8, pady=20)
        self.search_entry.bind("<Enter>", self.on_enter)
        self.search_entry.bind("<Leave>", self.on_leave)


    def _add_search_button(self):
        """Add the search button to the GUI."""
        button_frame = tk.Frame(self.master, bg='#ffffff')  # Set background to white
        button_frame.pack(pady=10)

        # Querlo Search Button
        search_btn = tk.Button(
            button_frame, text="Querlo Search", command=self.perform_search,
            bg="#faf5f5", fg="black", height=2, width=15, font=("Arial", 10), relief='flat'
        )
        search_btn.grid(row=0, column=0, padx=10)

        # Load Corpus Button
        load_corpus_btn = tk.Button(
            button_frame, text="Load Corpus", command=self.load_corpus,
            bg="#faf5f5", fg="black", height=2, width=15, font=("Arial", 10), relief='flat'
        )
        load_corpus_btn.grid(row=0, column=1, padx=10)

        # Message label for displaying warnings, initially empty
        self.warning_label = tk.Label(button_frame, text="", fg="red", bg='#ffffff', font=("Arial", 10))
        self.warning_label.grid(row=1, columnspan=2, pady=15)

    def load_corpus(self):
        """
        Load the corpus from a user-selected directory.
        
        Uses filedialog to allow the user to select a directory, then loads text and JSON documents
        from the selected directory into the corpus.
        """
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            corpus_path = Path(folder_selected)
            extension_factories = {
                '.txt': TextFileDocument.load_from,
                '.json': JsonDocument.load_from
            }
            self.corpus = DirectoryCorpus.load_directory(corpus_path, extension_factories)
            print(f"Corpus loaded from {corpus_path}. Total number of documents: {len(self.corpus)}")

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

    def on_enter(self, event):
        """
        Highlight the search box when the mouse enters.
        
        Args:
            event: The event object (not used, but required by Tkinter)
        """
        self.search_entry.config(highlightbackground='#A9A9A9')

    def on_leave(self, event):
        """
        Remove the highlight when the mouse leaves the search box.
        
        Args:
            event: The event object (not used, but required by Tkinter)
        """
        self.search_entry.config(highlightbackground='light gray')
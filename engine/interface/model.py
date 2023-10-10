from engine.documents import DocumentCorpus, DirectoryCorpus, TextFileDocument, JsonDocument, XMLDocument
from engine.text import BasicTokenProcessor, SpanishTokenProcessor, EnglishTokenStream, SpanishTokenStream
from engine.indexing import Index, PositionalInvertedIndex
from engine.querying import BooleanQueryParser
from tkinter import filedialog, Label, ttk
from pathlib import Path
from io import StringIO, TextIOWrapper
from datetime import timedelta
from langdetect import detect
from .decorators import threaded, threaded_value
import time
import threading
import re
import traceback
import queue
import io
import builtins

class CorpusManager:
    def __init__(self):
        self.corpus = None
        self.langauge = None
        self.p_i_index = PositionalInvertedIndex()
        self.eng_processor = BasicTokenProcessor()
        self.es_processor = SpanishTokenProcessor()

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
        self.language = self.detect_language(lang_content)

        # Process each document based on the detected language
        for i, doc_path in enumerate(self.corpus):
            # Detect Language
            if self.language == "en":
                tokens = EnglishTokenStream(doc_path.get_content())
                processor = self.eng_processor
            elif self.language == "es":
                tokens = SpanishTokenStream(doc_path.get_content())
                processor = self.es_processor
            else:
                continue

            position = 0
            for token in tokens:
                position += 1
                types = processor.process_token(token)
                for type in types:
                    term = processor.normalize_type(type)
                    self.p_i_index.addTerm(term, doc_path.id, position)

            if progress_callback:
                progress_callback(i)

        return self.p_i_index.getVocabulary()

    @staticmethod
    def detect_language(text):
        try:
            return detect(text)
        except:
            return None

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
        self.view = view
        self.search_entry = search_entry
        self.results_search_entry = results_search_entry
        self.home_warning_label = home_warning_label
        self.canvas = canvas

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
            lang = self.corpus_manager.language

            if lang == "en":
                normalized_query = self._process_english_query(raw_query)
            elif lang == "es":
                normalized_query = self._process_spanish_query(raw_query)
            
            postings = self._get_postings(normalized_query)

            if not postings:
                self.view.pages["ResultsPage"].display_no_results_warning()
                return

            self._display_search_results(postings, normalized_query)
        except SpecificException as e: 
            self._handle_search_error(e)

    def _corpus_ready(self):
        if not self.corpus_manager.corpus or not self.corpus_manager.p_i_index:
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

    def _process_english_query(self, raw_query):
        OPERATOR_PLUS = "+"
        terms = re.split(r'([+])', raw_query)
        token_processor = BasicTokenProcessor()  

        processed_query_parts = [
            term if term == OPERATOR_PLUS else (
                '"' + ' '.join(
                    token_processor.normalize_type(token)
                    for t in EnglishTokenStream(StringIO(term[1:-1]))  
                    for token in token_processor.process_token(t)
                ) + '"' if term.startswith('"') and term.endswith('"') else
                ' '.join(
                    token_processor.normalize_type(token)
                    for t in EnglishTokenStream(StringIO(term.strip()))
                    for token in token_processor.process_token(t)
                )
            ) for term in terms
        ]
        return ''.join(processed_query_parts)

    def _process_spanish_query(self, raw_query):
        OPERATOR_PLUS = "+"
        terms = re.split(r'([+])', raw_query)
        token_processor = SpanishTokenProcessor()  

        processed_query_parts = [
            term if term == OPERATOR_PLUS else (
                '"' + ' '.join(
                    token_processor.normalize_type(token)
                    for t in SpanishTokenStream(StringIO(term[1:-1]))  
                    for token in token_processor.process_token(t)
                ) + '"' if term.startswith('"') and term.endswith('"') else
                ' '.join(
                    token_processor.normalize_type(token)
                    for t in SpanishTokenStream(StringIO(term.strip()))
                    for token in token_processor.process_token(t)
                )
            ) for term in terms
        ]
        return ''.join(processed_query_parts)

    def _get_postings(self, normalized_query):
        print("Normalized:", normalized_query)
        parsed_query = BooleanQueryParser.parse_query(normalized_query)
        if not parsed_query:
            self.home_warning_label.config(text="Invalid Query. Please enter a valid search query.")
            return []
        print("Parsed:", parsed_query)
        print(self.corpus_manager.p_i_index)
        print(parsed_query.getPostings(self.corpus_manager.p_i_index))
        return parsed_query.getPostings(self.corpus_manager.p_i_index)

    def _display_search_results(self, postings, normalized_query):
        for posting in postings:
            doc = next((d for d in self.corpus_manager.corpus if d.id == posting.doc_id), None)
            if doc:
                # content_sentence = self.find_context_containing_query(''.join(doc.get_content()), normalized_query)
                self.view.pages["ResultsPage"].add_search_result_to_window(doc.id, doc.title, None)
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _handle_search_error(self, exception):
        self.view.pages["ResultsPage"].display_no_results_warning(str(exception))
        print("Error during search:", str(exception))
        traceback.print_exc()

    """
    import re
    @threaded_value
    def find_context_containing_query(self, document_content, raw_query, window_size=30):
        processed_query = self._process_query(raw_query)
        
        # Split by the '+' symbol to handle the OR operation
        or_terms = processed_query.split('+')
        
        # A set to store unique contexts to prevent duplication
        contexts = set()

        words_in_document = document_content.split()

        for or_term in or_terms:
            if or_term.startswith('"') and or_term.endswith('"'):
                # Phrase Literal
                phrase = or_term.strip('"').split()
                phrase_postings = self.corpus_manager.p_i_index.getPostings(phrase[0])
                for posting in phrase_postings:
                    for position in posting.positions:
                        if all(word in words_in_document[position + i: position + i + 1] for i, word in enumerate(phrase)):
                            start_idx = max(0, position - window_size // 2)
                            end_idx = min(position + len(phrase) + window_size // 2, len(words_in_document))
                            context = ' '.join(words_in_document[start_idx:end_idx])
                            contexts.add(context)
            else:
                # AND terms or Term Literals
                and_terms = or_term.split()
                print(and_terms)
                for term in and_terms:
                    term_postings = self.corpus_manager.p_i_index.getPostings(term)
                    if not term_postings: 
                        continue
                    for posting in term_postings:
                        for position in posting.positions:
                            start_idx = max(0, position - window_size // 2)
                            end_idx = min(position + window_size // 2 + 1, len(words_in_document))
                            context = ' '.join(words_in_document[start_idx:end_idx])
                            contexts.add(context)
                            print(contexts)

        return list(contexts)[0] if contexts else None
        """
from .model import SearchManager, CorpusManager, SearchManager, UIManager
from .view import SearchView


class SearchController:
    def __init__(self, master):
        """Initialize the SearchController."""
        self.master = master
        self.corpus_manager = CorpusManager(None)

        # Initialize the UIManager
        self.ui_manager = UIManager(
            master=self.master,
            view=None,
            corpus_manager=self.corpus_manager,
            search_manager=None,
        )

        # Initialize the SearchManager
        self.search_manager = SearchManager(
            corpus_manager=self.corpus_manager,
            preprocess=self.corpus_manager.preprocess,
            view=None,
            search_entry=None,
            results_search_entry=None,
            home_warning_label=None,
            canvas=None,
        )

        # Initialize the view
        self.view = SearchView(master, self, self.ui_manager)

        # Bind methods
        self.view.perform_search = self.ui_manager.perform_search_ui
        self.view.load_corpus = self.ui_manager.load_corpus_ui

        # Link the SearchManager with the proper view components after view is initialized
        self.search_manager.view = self.view
        self.search_manager.home_warning_label = self.view.pages[
            "HomePage"
        ].home_warning_label
        self.search_manager.search_entry = self.view.pages["HomePage"].search_entry
        self.search_manager.results_search_entry = self.view.pages[
            "ResultsPage"
        ].results_search_entry
        self.search_manager.results_frame = self.view.pages["ResultsPage"].results_frame

        # Update the UIManager's view reference
        self.ui_manager.view = self.view

        self.search_manager.initialize_disk_index()
        self.ui_manager.search_manager = self.search_manager

        self.corpus_manager.search_manager = self.search_manager

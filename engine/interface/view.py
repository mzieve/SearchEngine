from tkinter import filedialog, Label, ttk
import tkinter.font as font
from PIL import Image
import customtkinter # type: ignore

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
BG_COLOR = "#ffffff"
LOGO_COLOR = "#ff5733"
LOGO_FONT = ("Arial", 62)
LOGO_PADX = 100


class SearchView:
    def __init__(self, master, controller, ui_manager):
        """Initialize the GUI components."""
        self.master = master
        self.controller = controller
        self.ui_manager = ui_manager
        self.pages = {}
        self._configure_master()
        self._initialize_frames()

    def _configure_master(self):
        """Configures the master window."""
        self.master.configure(bg=BG_COLOR)
        self._center_window(WINDOW_WIDTH, WINDOW_HEIGHT)

    def _initialize_frames(self):
        """Initializes the primary frames of the GUI."""
        self.container = customtkinter.CTkFrame(self.master)

        self.container.grid(row=0, column=0, sticky="nsew")
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)

        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        # Instantiate each page and store in the pages dictionary
        self.pages["HomePage"] = HomePage(self.container, self.controller)
        self.pages["ResultsPage"] = ResultsPage(self.container, self.controller)

        # Default to showing the home page
        self.show_page("HomePage")

    def _center_window(self, width, height):
        """Center the application window on the screen."""
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x_coordinate = (screen_width - width) // 2
        y_coordinate = (screen_height - height) // 2
        self.master.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")

    def show_page(self, page_name):
        """Show Pages"""
        for page in self.pages.values():
            page.grid_forget()

        if page_name == "HomePage":
            self.pages[page_name].grid(
                row=0,
                column=0,
                sticky="nsew",
                padx=(WINDOW_WIDTH // 4),
                pady=(WINDOW_HEIGHT // 4),
            )
        elif page_name == "ResultsPage":
            self.pages[page_name].grid(row=0, column=0, sticky="nsew")


class HomePage(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        customtkinter.CTkFrame.__init__(self, parent)
        self.controller = controller

        self.centered_frame = customtkinter.CTkFrame(self)
        self.centered_frame.grid(row=0, column=0, sticky="nsew")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.centered_frame.columnconfigure(0, weight=1)
        self.centered_frame.rowconfigure(0, weight=1)
        self.centered_frame.rowconfigure(1, weight=1)
        self.centered_frame.rowconfigure(2, weight=1)
        self.centered_frame.rowconfigure(3, weight=1)

        self._add_home_logo()
        self._add_home_search_entry()
        self._add_search_button()

    def _add_home_logo(self):
        """Add the application logo to the GUI."""
        logo_label = customtkinter.CTkLabel(
            self.centered_frame,
            text="Querlo",
            font=("Arial", 62),
            fg_color="#7236bf",
            padx=10,
            pady=10,
            text_color="white",
        )
        logo_label.grid(row=0, column=0, pady=(0, 5), padx=100, columnspan=3)

    def _add_home_search_entry(self, query=""):
        """Add the search entry box to the GUI."""
        self.search_entry = customtkinter.CTkEntry(
            self.centered_frame, width=500, corner_radius=30
        )
        self.search_entry.grid(row=1, column=0, columnspan=3, ipady=8, pady=5)
        self.search_entry.insert(0, query)
        self.search_entry.bind(
            "<Return>",
            lambda event=None: self.controller.ui_manager.perform_search_ui(),
        )

    def _add_search_button(self):
        """Add the search button to the GUI."""
        button_frame = customtkinter.CTkFrame(
            self.centered_frame, fg_color="transparent", width=100
        )
        button_frame.grid(row=2, column=0, columnspan=3, pady=5)

        search_btn = customtkinter.CTkButton(
            button_frame,
            text="Querlo Search",
            command=self.controller.ui_manager.perform_search_ui,
            height=40,
            width=120,
            font=("Arial", 14),
            fg_color="#4a4a4a",
            hover_color="#636363",
        )
        search_btn.grid(row=0, column=0, padx=10)

        load_corpus_btn = customtkinter.CTkButton(
            button_frame,
            text="Load Corpus",
            command=self.controller.ui_manager.load_corpus_ui,
            height=40,
            width=120,
            font=("Arial", 14),
            fg_color="#4a4a4a",
            hover_color="#636363",
        )
        load_corpus_btn.grid(row=0, column=1, padx=10)

        self.home_warning_label = customtkinter.CTkLabel(
            button_frame, text="", font=("Arial", 10)
        )
        self.home_warning_label.grid(row=1, columnspan=2, pady=10)


class ResultsPage(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        customtkinter.CTkFrame.__init__(self, parent)
        self.controller = controller
        self.displayed_results = []

        self.top_frame = customtkinter.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, sticky="nsew", columnspan=2)

        # Configure the row and column weights
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Configure the row and column weights for top frame
        self.top_frame.columnconfigure(0, weight=0)
        self.top_frame.columnconfigure(1, weight=1)
        self.top_frame.rowconfigure(0, weight=1)

        self.results_search_entry = None

        # Add result frame to canvas
        self.results_frame = customtkinter.CTkScrollableFrame(self)
        self.results_frame.grid(
            row=1, column=0, sticky="nsew", columnspan=2, pady=(5, 0)
        )

        # Label for displaying the number of results
        self.results_count_label = None

    def show_results_page(self, query):
        """Show the Logo and Entry for Results"""
        self._add_results_logo()
        self._add_results_search_entry(query)

    def _add_results_logo(self):
        logo_label = customtkinter.CTkLabel(
            self.top_frame,
            text="Querlo",
            font=("Arial", 26),
            fg_color="#7236bf",
            padx=10,
            pady=10,
            text_color="white",
        )
        logo_label.grid(row=0, column=0, sticky="w", padx=(50, 45), pady=25)

    def _add_results_search_entry(self, query):
        self.results_search_entry = customtkinter.CTkEntry(
            self.top_frame, width=500, corner_radius=25
        )
        self.results_search_entry.grid(row=0, column=1, sticky="w")
        self.results_search_entry.insert(0, query)
        self.results_search_entry.bind(
            "<Return>",
            lambda event=None: self.controller.ui_manager.perform_search_ui(),
        )

    def display_no_results_warning(self, error_message=None):
        """Display the no results message inside the results frame."""
        result_frame = customtkinter.CTkFrame(self.results_frame)
        result_frame.grid(sticky="ew", padx=150)

        # Load the image
        self.image = customtkinter.CTkImage(dark_image=Image.open("./img/pow.png"))
        image_label = customtkinter.CTkLabel(result_frame, image=self.image, text="")
        image_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        message = "Your search did not match any Documents \n\nSuggestions: \n\n\u2022Make sure all keywords are spelled correctly. \n\u2022Try different keywords \n\u2022Try more general keywords."

        if error_message:
            message += f"\n\nError: {error_message}"

        customtkinter.CTkLabel(
            result_frame,
            text=message,
            font=("Arial", 10),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=5)

        self.displayed_results.append(result_frame)

    def add_search_result_to_window(self, doc_id, doc_title):
        """Display the Results"""
        result_frame = customtkinter.CTkFrame(self.results_frame)
        result_frame.grid(
            sticky="ew",
            padx=150,
        )

        customtkinter.CTkLabel(
            result_frame,
            text=f"Document ID# {doc_id}",
            font=("Helvetica", 11),
        ).grid(row=0, column=0, sticky="w")

        customtkinter.CTkLabel(
            result_frame, text=doc_title, font=("Helvetica", 20), text_color="#5291f7"
        ).grid(row=1, column=0, sticky="w", pady=(0, 25))

        self.displayed_results.append(result_frame)

    def clear_results(self):
        """Clear all displayed search results and reset Canvas's scroll region."""
        for result_frame in self.displayed_results:
            result_frame.destroy()
        self.displayed_results.clear()

    def update_results_count(self, count):
        if self.results_count_label:
            self.results_count_label.destroy()

        message = f"About {count} results"
        self.results_count_label = customtkinter.CTkLabel(
            self.results_frame,
            text=message,
            font=("Helvetica", 11),
        )
        self.results_count_label.grid(sticky="w", padx=150, pady=(5, 0))

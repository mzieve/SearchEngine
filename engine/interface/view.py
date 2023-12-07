from tkinter import filedialog, Label, ttk
import tkinter.font as font
from PIL import Image, ImageSequence
import customtkinter  # type: ignore
from customtkinter import CTkScrollableFrame
from itertools import cycle
import tkinter as tk

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
        self.master.minsize(1000, 800)

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

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.centered_frame = customtkinter.CTkFrame(self, bg_color="#2b2b2b")
        self.centered_frame.grid(row=0, column=0, sticky="nsew")
        self.centered_frame.configure(width=400, height=400)

        self.centered_frame.columnconfigure(0, weight=1)
        self.centered_frame.rowconfigure(0, weight=1)
        self.centered_frame.rowconfigure(1, weight=0, minsize=100)
        self.centered_frame.rowconfigure(2, weight=0, minsize=100)
        self.centered_frame.rowconfigure(3, weight=0, minsize=100)
        self.centered_frame.rowconfigure(4, weight=0, minsize=100)
        self.centered_frame.rowconfigure(5, weight=1)

        self._add_home_logo()
        self._add_home_search_entry()
        self._add_search_button()

    def _add_home_logo(self):
        """Add the application logo to the GUI."""
        logo_label = customtkinter.CTkLabel(
            self.centered_frame,
            text="Querlo",
            font=("Arial", 68),
            fg_color="#7236bf",
            padx=10,
            pady=10,
            text_color="white",
        )
        logo_label.grid(row=1, column=0, pady=(0, 15), padx=100, columnspan=3)

    def _add_home_search_entry(self, query=""):
        """Add the search entry box to the GUI."""
        self.search_entry = customtkinter.CTkEntry(
            self.centered_frame, width=500, corner_radius=20, fg_color="#2b2b2b"
        )
        self.search_entry.grid(row=2, column=0, columnspan=3, ipady=8, pady=(0, 15))
        self.search_entry.insert(0, query)
        self.search_entry.bind(
            "<Return>",
            lambda event=None: self.controller.ui_manager.perform_search_ui(),
        )

    def _add_search_button(self):
        """Add the search button to the GUI."""
        button_frame = customtkinter.CTkFrame(
            self.centered_frame, fg_color="transparent"
        )
        button_frame.grid(row=3, column=0, columnspan=3)

        search_btn = customtkinter.CTkButton(
            button_frame,
            text="Querlo Search",
            command=self.controller.ui_manager.perform_search_ui,
            height=40,
            width=120,
            font=("Arial", 14),
            fg_color="#666666",
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
            fg_color="#666666",
            hover_color="#636363",
        )
        load_corpus_btn.grid(row=0, column=1, padx=10)

        self.home_warning_label = customtkinter.CTkLabel(
            button_frame, text="", font=("Arial", 14)
        )
        self.home_warning_label.grid(row=1, columnspan=2, pady=(20, 0))


class ResultsPage(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        customtkinter.CTkFrame.__init__(self, parent)
        self.controller = controller
        self.displayed_results = []
        self.results_count_label = None

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
        self.results_frame = LazyLoading(self, [])
        self.results_frame.grid(
            row=1, column=0, sticky="nsew", columnspan=2, pady=(5, 0)
        )

        # Label for displaying the number of results
        self.results_count_label = None

    def show_results_page(self, query):
        """Show the Logo and Entry for Results"""
        logo_label = customtkinter.CTkLabel(
            self.top_frame,
            text="Querlo",
            font=("Arial", 26),
            fg_color="#7236bf",
            padx=10,
            pady=10,
            text_color="white",
        )

        if not self.results_search_entry:
            self.results_search_entry = customtkinter.CTkEntry(
                self.top_frame,
                width=600,
                height=40,
                corner_radius=25,
                fg_color="#2b2b2b",
            )
            self.results_search_entry.grid(row=0, column=1, sticky="w")

            self.results_search_entry.bind(
                "<Return>",
                lambda event=None: self.controller.ui_manager.perform_search_ui(),
            )
        else:
            self.results_search_entry.delete(0, "end")

        self.results_search_entry.insert(0, query)
        logo_label.grid(row=0, column=0, sticky="w", padx=(50, 45), pady=25)

    def display_no_results_warning(self, query, error_message=None):
        """Display the no results message inside the results frame."""
        result_frame = customtkinter.CTkFrame(self.results_frame)
        animated_gif = AnimatedGIF(
            result_frame, path="./img/marvel.gif", size=(150, 150)
        )
        message = f"Your search - {query} - did not match any Documents \n\nSuggestions: \n\n\u2022 Make sure all keywords are spelled correctly.\n\u2022 Try different keywords\n\u2022 Try more general keywords."
        if error_message:
            message += f"\n\nError: {error_message}"

        result_label = customtkinter.CTkLabel(
            result_frame,
            text="About 0 results",
            font=("Helvetica", 11),
        )

        message_label = customtkinter.CTkLabel(
            result_frame, text=message, font=("Helvetica", 14), justify="left"
        )

        self.update_idletasks()

        result_frame.grid(row=1, column=0, columnspan=2)
        result_label.grid(row=0, column=0, sticky="w", padx=150, pady=(5, 0))
        message_label.grid(row=1, column=0, pady=5, padx=150)

        self.displayed_results.append(result_frame)

    def clear_results(self):
        """Clear all displayed search results and reset Canvas's scroll region."""
        self.results_frame.destroy()

        self.results_frame = LazyLoading(self, [])
        self.results_frame.grid(
            row=1, column=0, sticky="nsew", columnspan=2, pady=(5, 0)
        )


class LazyLoading(customtkinter.CTkScrollableFrame):
    def __init__(self, master, data_items, chunk_size=15, *args, **kwargs):
        """Initializes the LazyLoading frame with data items and settings."""
        super().__init__(master, *args, **kwargs)

        self.data_items = data_items
        self.chunk_size = chunk_size
        self.last_loaded_index = -1

        self.load_initial_widgets()
        self.periodic_check_scroll()

    def update_results_count(self, count):
        """Updates the results count label with the given count."""
        if hasattr(self, "results_count_label") and self.results_count_label:
            self.results_count_label.destroy()

        message = f"About {count} results"
        self.results_count_label = customtkinter.CTkLabel(
            self,
            text=message,
            font=("Helvetica", 11),
        )

        self.results_count_label.grid(
            row=0, column=0, sticky="w", padx=150, pady=(5, 0)
        )

    def load_initial_widgets(self):
        """Loads the initial set of widgets based on the chunk size."""
        end = min(self.chunk_size, len(self.data_items))
        self.load_new_widgets(0, end)

    def periodic_check_scroll(self):
        """Periodically checks the scroll position to load more items if needed."""
        yview = self._parent_canvas.yview()
        if yview[1] >= 0.95:
            self.load_next_chunk()

        self.after(100, self.periodic_check_scroll)

    def load_next_chunk(self):
        """Loads the next chunk of data items as widgets."""
        start = self.last_loaded_index + 1
        end = start + self.chunk_size
        self.load_new_widgets(start, end)

    def load_new_widgets(self, start, end):
        """Loads widgets for data items in the given range (start to end)."""
        for i in range(start, end):
            if i < len(self.data_items):
                widget = self.create_widget_from_data(self.data_items[i])
                widget.grid(row=i + 1, column=0, sticky="nsew")

        self.last_loaded_index = end - 1

    def create_widget_from_data(self, data):
        """Creates a widget for a given data item and returns it."""
        parts = data.split(" - ")
        doc_id_str = parts[0].replace("Document ID# ", "")
        doc_title = parts[1]

        doc_id = int(doc_id_str)

        result_frame = customtkinter.CTkFrame(self)
        result_frame.grid(sticky="ew", padx=150)

        customtkinter.CTkLabel(
            result_frame,
            text=f"Document ID# {doc_id}",
            font=("Helvetica", 11),
        ).grid(row=0, column=0, sticky="w")

        customtkinter.CTkLabel(
            result_frame, text=doc_title, font=("Helvetica", 20), text_color="#5291f7"
        ).grid(row=1, column=0, sticky="w", pady=(0, 25))

        return result_frame


class AnimatedGIF:
    def __init__(self, master, path, size):
        self.frames = [
            frame.copy() for frame in ImageSequence.Iterator(Image.open(path))
        ]
        self.frames_cycle = cycle(self.frames)
        self.current_image = customtkinter.CTkImage(
            light_image=next(self.frames_cycle), size=size
        )
        self.image_label = customtkinter.CTkLabel(
            master, image=self.current_image, text=""
        )
        self.image_label.grid(row=2, column=0, sticky="w", padx=150, pady=(25, 0))
        self._animate()

    def _animate(self):
        next_image = customtkinter.CTkImage(
            light_image=next(self.frames_cycle), size=(175, 175)
        )
        self.image_label.configure(image=next_image)
        self.image_label.image = next_image
        self.image_label.after(15, self._animate)

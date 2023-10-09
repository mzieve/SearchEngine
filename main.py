import tkinter as tk
from engine.interface.controller import SearchController
import sys

if __name__ == "__main__":
    root = tk.Tk()
    app = SearchController(root)
    root.mainloop()
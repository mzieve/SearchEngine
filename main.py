import tkinter as tk
from engine.interface import SearchEngineGUI
import sys

if __name__ == "__main__":
    root = tk.Tk()
    app = SearchEngineGUI(root)
    root.mainloop()
import tkinter as tk
from interface.interface import SearchEngineGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = SearchEngineGUI(root)
    root.mainloop()
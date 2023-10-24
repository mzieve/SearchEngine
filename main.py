from engine.interface.controller import SearchController
import customtkinter # type: ignore
import sys

if __name__ == "__main__":
    customtkinter.set_appearance_mode("dark")
    root = customtkinter.CTk()
    app = SearchController(root)
    root.mainloop()

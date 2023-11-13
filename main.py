from engine.interface.controller import SearchController
import customtkinter # type: ignore
import sys

if __name__ == "__main__":
    customtkinter.set_appearance_mode("dark")
    root = customtkinter.CTk()
    root.title("Querlo")
    #root.iconphoto(False, customtkinter.PhotoImage(file="img/logo.png"))
    app = SearchController(root)
    root.mainloop()

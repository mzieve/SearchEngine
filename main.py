from engine.interface.controller import SearchController
import customtkinter  # type: ignore

if __name__ == "__main__":
    customtkinter.set_appearance_mode("dark")
    root = customtkinter.CTk()
    root.title("Querlo")
    app = SearchController(root)
    root.mainloop()

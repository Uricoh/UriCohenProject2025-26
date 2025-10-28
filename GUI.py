import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk
import protocol


class GUI:
    def __init__(self):
        self._root = tk.Tk()
        self._bg_pimage: str = ""
        self.create_ui()
        self._started: bool = False

    def create_ui(self):
        self._root.title("Currency Converter - Start Page")
        self._root.geometry(f"{protocol.size1}x{protocol.size2}")

        # Show background image
        bg_image = Image.open(protocol.bg_path)
        bg_reimage = bg_image.resize((protocol.size1, protocol.size2))
        self._bg_pimage: PhotoImage = ImageTk.PhotoImage(bg_reimage)
        bg_label = tk.Label(self._root, image=self._bg_pimage)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def run(self):
        self._root.mainloop()

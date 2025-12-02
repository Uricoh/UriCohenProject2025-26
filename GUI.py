import tkinter as tk
import protocol
from tkinter import PhotoImage
from PIL import Image, ImageTk


# Should NEVER be inherited by frames
class GUI:
    def __init__(self):
        self._root = tk.Tk()
        self._root.title("Currency Converter - Start Page")
        self._root.geometry(f"{protocol.width}x{protocol.height}")

        # Show background image
        bg_image = Image.open(protocol.bg_path)
        bg_reimage = bg_image.resize((protocol.width, protocol.height))
        self.bg_pimage: PhotoImage = ImageTk.PhotoImage(bg_reimage)
        self.bg_label = tk.Label(self._root, image=self.bg_pimage)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Configure started flag
        self._started: bool = False

    def run(self):
        self._root.mainloop()

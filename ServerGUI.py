import tkinter as tk

import protocol
from ServerBL import *
from tkinter import PhotoImage
from PIL import Image, ImageTk


class ServerGUI:
    def __init__(self, server_bl):
        # Get BL
        self.server_bl = server_bl

        # Create root
        self._root = tk.Tk()
        self._root.title(f"{protocol.APP_NAME} - Server")
        self._root.geometry(f"{protocol.SCREEN_WIDTH}x{protocol.SCREEN_HEIGHT}")

        # Show background image
        _bg_image = Image.open(protocol.BG_PATH)
        _bg_reimage = _bg_image.resize(protocol.SCREEN_AREA)
        self._bg_pimage: PhotoImage = ImageTk.PhotoImage(_bg_reimage)
        self._bg_label = tk.Label(self._root, image=self._bg_pimage)
        self._bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create label
        self._server_label = tk.Label(self._root, text="Server", font=(protocol.FONT_NAME, 2 * protocol.FONT_SIZE),
                                      bg='yellow')

        # Create buttons
        self._start_button = tk.Button(self._root, text="Start", font=protocol.FONT, command=self.on_click_start_gui)
        self._stop_button = tk.Button(self._root, text="Stop", font=protocol.FONT, command=self.on_click_stop_gui)
        protocol.reverse_button(self._stop_button)

        # Place objects
        self._server_label.place(x=3 * protocol.LABELS_X, y=100)
        self._start_button.place(x=protocol.BUTTONS_X, y=80)
        self._stop_button.place(x=protocol.BUTTONS_X, y=230)

    def on_click_start_gui(self):
        protocol.reverse_many_buttons((self._start_button, self._stop_button))
        self.server_bl.on_click_start()

    def on_click_stop_gui(self):
        protocol.reverse_many_buttons((self._start_button, self._stop_button))
        self.server_bl.on_click_stop()

    def run(self):
        self._root.mainloop()


if __name__ == "__main__":
    # Run server
    server_bl = ServerBL()
    server_screen: ServerGUI = ServerGUI(server_bl)
    server_screen.run()
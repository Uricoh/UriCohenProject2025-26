import tkinter as tk
from ServerBL import *
from tkinter import PhotoImage
from PIL import Image, ImageTk


class ServerGUI(ServerBL):
    def __init__(self):
        # Constructor
        super().__init__()

        # Create root
        self._root = tk.Tk()
        self._root.title(f"{protocol.app_name} - Server")
        self._root.geometry(f"{protocol.width}x{protocol.height}")

        # Show background image
        bg_image = Image.open(protocol.bg_path)
        bg_reimage = bg_image.resize((protocol.width, protocol.height))
        self.bg_pimage: PhotoImage = ImageTk.PhotoImage(bg_reimage)
        self.bg_label = tk.Label(self._root, image=self.bg_pimage)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create label
        self._server_label = tk.Label(self._root, text="Server", font=(protocol.font_name, 2 * protocol.font_size),
                                      bg='yellow')

        # Create buttons
        self._start_button = tk.Button(self._root, text="Start", font=protocol.font, command=self.on_click_start_gui)
        self._stop_button = tk.Button(self._root, text="Stop", font=protocol.font, command=self.on_click_stop_gui)
        protocol.reverse_button(self._stop_button)

        # Place objects
        self._server_label.place(x=3 * protocol.labels_x, y=100)
        self._start_button.place(x=protocol.buttons_x, y=80)
        self._stop_button.place(x=protocol.buttons_x, y=230)

    def on_click_start_gui(self):
        protocol.reverse_many_buttons((self._start_button, self._stop_button))
        self.on_click_start()

    def on_click_stop_gui(self):
        protocol.reverse_many_buttons((self._start_button, self._stop_button))
        self.on_click_stop()

    def run(self):
        self._root.mainloop()


if __name__ == "__main__":
    # Run server
    server_screen: ServerGUI = ServerGUI()
    server_screen.run()
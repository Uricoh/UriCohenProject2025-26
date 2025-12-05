import tkinter as tk
from GUI import GUI
from ServerBL import *


class ServerGUI(GUI, ServerBL):
    def __init__(self):
        # Constructors
        GUI.__init__(self)
        ServerBL.__init__(self)

        # Create buttons
        self._start_button = tk.Button(self._root, text="Start", font=protocol.font, command=self.on_click_start_gui)
        self._stop_button = tk.Button(self._root, text="Stop", font=protocol.font, command=self.on_click_stop_gui)
        protocol.reverse_button(self._stop_button)

        # Place buttons
        self._start_button.place(x=protocol.buttons_x, y=80)
        self._stop_button.place(x=protocol.buttons_x, y=230)


    def on_click_start_gui(self):
        protocol.reverse_many_buttons((self._start_button, self._stop_button))
        self.on_click_start()

    def on_click_stop_gui(self):
        protocol.reverse_many_buttons((self._start_button, self._stop_button))
        self.on_click_stop()


if __name__ == "__main__":
    # Run server
    server_screen: ServerGUI = ServerGUI()
    server_screen.run()

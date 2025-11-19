import tkinter as tk
from GUI import GUI
from ServerBL import *


class ServerGUI(GUI, ServerBL):
    def __init__(self):
        GUI.__init__(self)
        ServerBL.__init__(self)

        # Create buttons
        self._start_button = tk.Button(self._root, text="Start", font=protocol.font, command=self.on_click_start_gui)
        self._stop_button = tk.Button(self._root, text="Stop", font=protocol.font, command=self.on_click_stop_gui)

        # Place buttons
        self._start_button.place(x=protocol.buttons_x, y=80)
        self._stop_button.place(x=protocol.buttons_x, y=230)

        self.first: bool = True

        # Manage buttons
        self._manage_buttons()

    def _manage_buttons(self):
        if self._started:
            self._start_button.config(state=tk.DISABLED)
            self._stop_button.config(state=tk.NORMAL)
        else:
            self._start_button.config(state=tk.NORMAL)
            self._stop_button.config(state=tk.DISABLED)
        if self.first:
            self.first = False
        else:
            protocol.logger.info("[SERVERGUI] - Buttons reversed")

    def on_click_start_gui(self):
        self._started = True
        self._manage_buttons()
        ServerBL.on_click_start(self)

    def on_click_stop_gui(self):
        self._started = False
        self._manage_buttons()
        ServerBL.on_click_stop(self)


if __name__ == "__main__":
    server_screen: ServerGUI = ServerGUI()
    server_screen.run()

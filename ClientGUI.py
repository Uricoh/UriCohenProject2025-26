import tkinter as tk
import protocol
from GUI import GUI
import json
from ClientBL import ClientBL


class ClientGUI(GUI, ClientBL):
    def __init__(self):
        GUI.__init__(self)
        ClientBL.__init__(self)

        # Create labels
        username_label = tk.Label(self._root, text="Username:", font=protocol.font)
        password_label = tk.Label(self._root, text="Password:", font=protocol.font)

        # Create text fields
        self._username_text = tk.Entry(self._root, width=protocol.text_width, font=protocol.font)
        self._password_text = tk.Entry(self._root, width=protocol.text_width, font=protocol.font)

        # Create buttons
        self._start_button = tk.Button(self._root, text="Start", font=protocol.font, command=self.on_click_start_gui)
        self._stop_button = tk.Button(self._root, text="Stop", font=protocol.font, command=self.on_click_stop_gui)
        self._signup_button = tk.Button(self._root, text="Sign up", font=protocol.font, command=self.on_click_signup_gui)
        self._login_button = tk.Button(self._root, text="Log in", font=protocol.font)

        # Place objects
        username_label.place(x=protocol.labels_x, y=20)
        password_label.place(x=protocol.labels_x, y=220)
        self._username_text.place(x=protocol.labels_x, y=80)
        self._password_text.place(x=protocol.labels_x, y=280)
        self._start_button.place(x=protocol.buttons_x, y=80)
        self._stop_button.place(x=protocol.buttons_x, y=230)
        self._signup_button.place(x=protocol.buttons_x, y=380)
        self._login_button.place(x=protocol.buttons_x, y=530)

        # Create username and password
        self._username = None
        self._password = None

        # Manage buttons
        self._manage_buttons(first=True)

    def _manage_buttons(self, first: bool):
        if self._started:
            self._start_button.config(state=tk.DISABLED)
            self._stop_button.config(state=tk.NORMAL)
            self._signup_button.config(state=tk.NORMAL)
            self._login_button.config(state=tk.NORMAL)
        else:
            self._start_button.config(state=tk.NORMAL)
            self._stop_button.config(state=tk.DISABLED)
            self._signup_button.config(state=tk.DISABLED)
            self._login_button.config(state=tk.DISABLED)
        if not first:
            self._logger.info("[CLIENTGUI] - Buttons reversed")

    def on_click_start_gui(self):
        self._started = True
        self._manage_buttons(first=False)
        ClientBL.on_click_start(self)

    def on_click_stop_gui(self):
        self._started = False
        self._manage_buttons(first=False)
        ClientBL.on_click_stop(self)

    def on_click_signup_gui(self):
        self._username = self._username_text.get()
        self._password = self._password_text.get()
        self._logger.info(f"[CLIENTGUI] - Username: {self._username_text.get()}")
        self._logger.info(f"[CLIENTGUI] - Password: {self._password_text.get()}")
        user_data = (self._username, self._password)
        json_data = json.dumps(user_data)
        self._logger.info("[CLIENTGUI] - JSON made")
        self._socket.sendall(json_data.encode('utf-8'))
        self._logger.info("[CLIENTGUI] - Data sent to server")


if __name__ == "__main__":
    client_screen: ClientGUI = ClientGUI()
    client_screen.run()

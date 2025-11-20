import tkinter as tk
import protocol
import json
from ClientBL import ClientBL
import threading
from tkinter import PhotoImage
from PIL import Image, ImageTk
from typing import cast


class LoginFrame(ClientBL, tk.Frame):
    def __init__(self):
        ClientBL.__init__(self)
        tk.Frame.__init__(self)

        # Show background image
        bg_image = Image.open(protocol.bg_path)
        bg_reimage = bg_image.resize((protocol.size1, protocol.size2))
        self.bg_pimage: PhotoImage = ImageTk.PhotoImage(bg_reimage)
        self.bg_label = tk.Label(self, image=self.bg_pimage)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self._started: bool = False

        # Create labels
        username_label = tk.Label(self, text="Username:", font=protocol.font)
        password_label = tk.Label(self, text="Password:", font=protocol.font)

        # Create text fields
        self._username_text = tk.Entry(self, width=protocol.text_width, font=protocol.font)
        self._password_text = tk.Entry(self, width=protocol.text_width, font=protocol.font)

        # Create buttons
        self._start_button = tk.Button(self, text="Start", font=protocol.font, command=self.on_click_start_gui)
        self._stop_button = tk.Button(self, text="Stop", font=protocol.font, command=self.on_click_stop_gui)
        self._signup_button = tk.Button(self, text="Sign up", font=protocol.font, command=self.on_click_signup_gui)
        self._login_button = tk.Button(self, text="Log in", font=protocol.font, command=self.on_click_login_gui)

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

        self.first = True

        # Manage buttons
        self._manage_buttons()

        self.listen_thread = None

    def _manage_buttons(self):
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
        if self.first:
            self.first = False
        else:
            protocol.logger.info("[CLIENTGUI] - Buttons reversed")

    def on_click_start_gui(self):
        self._started = True
        self._manage_buttons()
        ClientBL.on_click_start(self)
        protocol.logger.info(f"[CLIENTGUI] - Socket ID: {id(self._socket)}")
        self.listen_thread = threading.Thread(target=self.listen, daemon=True)
        self.listen_thread.start()

    def on_click_stop_gui(self):
        self._started = False
        self._manage_buttons()
        ClientBL.on_click_stop(self)

    def on_click_signup_gui(self):
        # Get username and password
        self._username = self._username_text.get()
        self._password = self._password_text.get()

        protocol.logger.info(f"[CLIENTGUI] - Username: {self._username_text.get()}")
        protocol.logger.info(f"[CLIENTGUI] - Password: {self._password_text.get()}")

        # Make JSON
        user_data = ("SIGNUP", self._username, self._password)
        json_data = json.dumps(user_data)
        protocol.logger.info("[CLIENTGUI] - JSON made")

        # Send JSON to server
        self._socket.sendall(json_data.encode('utf-8'))
        protocol.logger.info("[CLIENTGUI] - Data sent to server")

    def on_click_login_gui(self):
        # Get username and password
        self._username = self._username_text.get()
        self._password = self._password_text.get()

        protocol.logger.info(f"[CLIENTGUI] - Username: {self._username_text.get()}")
        protocol.logger.info(f"[CLIENTGUI] - Password: {self._password_text.get()}")

        # Make JSON
        user_data = ("LOGIN", self._username, self._password)
        json_data = json.dumps(user_data)
        protocol.logger.info("[CLIENTGUI] - JSON made")

        # Send JSON to server
        self._socket.sendall(json_data.encode('utf-8'))
        protocol.logger.info("[CLIENTGUI] - Data sent to server")

    def listen(self):
        while True:
            try:
                data = self._socket.recv(1024).decode('utf-8')
                if data == "LOGIN":
                    protocol.logger.info("[CLIENTGUI] - Received login")
                    cast(ClientApp, self.master).show_main()
            except OSError:
                break


class MainFrame(ClientBL, tk.Frame):
    def __init__(self, old_bl):
        tk.Frame.__init__(self)
        self._socket = old_bl.get_socket()
        protocol.logger.info(f"[CLIENTGUI] - Socket ID: {id(self._socket)}")

        # Show background image
        bg_image = Image.open(protocol.bg_path)
        bg_reimage = bg_image.resize((protocol.size1, protocol.size2))
        self.bg_pimage: PhotoImage = ImageTk.PhotoImage(bg_reimage)
        self.bg_label = tk.Label(self, image=self.bg_pimage)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self._started: bool = False

        self._stop_button = tk.Button(self, text="Stop", font=protocol.font, command=self.on_click_stop_gui)
        self._stop_button.place(x=protocol.buttons_x, y=230)

    def on_click_stop_gui(self):
        # More commands to follow
        ClientBL.on_click_stop(self)

class ClientApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Currency Converter - Start Page")
        self.geometry(f"{protocol.size1}x{protocol.size2}")
        self._current_frame = LoginFrame()
        self._current_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    def show_main(self):
        bl = self._current_frame
        self._current_frame.destroy()
        self._current_frame = MainFrame(bl)
        self._current_frame.place(relx=0, rely=0, relwidth=1, relheight=1)


if __name__ == "__main__":
    app: ClientApp = ClientApp()
    app.mainloop()
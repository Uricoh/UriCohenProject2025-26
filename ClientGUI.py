# Imports
import tkinter as tk
import protocol
import json
from ClientBL import ClientBL
import threading
from tkinter import PhotoImage
from PIL import Image, ImageTk
from typing import cast


class StartFrame(tk.Frame):
    def __init__(self, client_bl):
        # Constructors
        super().__init__()
        self.client_bl = client_bl

        # Show background image
        bg_image = Image.open(protocol.bg_path)
        bg_reimage = bg_image.resize((protocol.width, protocol.height))
        self.bg_pimage: PhotoImage = ImageTk.PhotoImage(bg_reimage)
        self.bg_label = tk.Label(self, image=self.bg_pimage)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create buttons
        self._signup_button = tk.Button(self, text="Sign up", font=protocol.font, command=self.on_click_signup_gui)
        self._login_button = tk.Button(self, text="Log in", font=protocol.font, command=self.on_click_login_gui)

        # Place buttons
        self._signup_button.place(x=protocol.buttons_x, y=80)
        self._login_button.place(x=protocol.buttons_x, y=230)

        # Configure started flag
        self._started: bool = False

    def on_click_signup_gui(self):
        cast(ClientApp, self.master).show_frame(SignupFrame)

    def on_click_login_gui(self):
        cast(ClientApp, self.master).show_frame(LoginFrame)


class LoginFrame(tk.Frame):
    def __init__(self, client_bl):
        # Constructors
        super().__init__()
        self.client_bl = client_bl

        # Show background image
        bg_image = Image.open(protocol.bg_path)
        bg_reimage = bg_image.resize((protocol.width, protocol.height))
        self.bg_pimage: PhotoImage = ImageTk.PhotoImage(bg_reimage)
        self.bg_label = tk.Label(self, image=self.bg_pimage)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create labels
        username_label = tk.Label(self, text="Username:", font=protocol.font)
        password_label = tk.Label(self, text="Password:", font=protocol.font)

        # Create text fields
        self._username_text = tk.Entry(self, width=protocol.text_width, font=protocol.font)
        self._password_text = tk.Entry(self, width=protocol.text_width, font=protocol.font, show='•')

        # Create buttons
        self._start_button = tk.Button(self, text="Start", font=protocol.font, command=self.on_click_start_gui)
        self._stop_button = tk.Button(self, text="Stop", font=protocol.font, command=self.on_click_stop_gui)
        self._login_button = tk.Button(self, text="Log in", font=protocol.font, command=self.on_click_login_gui)
        self._back_button = tk.Button(self, text="Back", font=protocol.font, command=self.on_click_back_gui)

        # Place objects
        username_label.place(x=protocol.labels_x, y=20)
        password_label.place(x=protocol.labels_x, y=220)
        self._username_text.place(x=protocol.labels_x, y=80)
        self._password_text.place(x=protocol.labels_x, y=280)
        self._start_button.place(x=protocol.buttons_x, y=80)
        self._stop_button.place(x=protocol.buttons_x, y=230)
        self._login_button.place(x=protocol.buttons_x, y=380)
        self._back_button.place(x=protocol.buttons_x, y=530)

        # Create username, password and email
        self._username = None
        self._password = None

        # First, used for manage_buttons()
        self.first = True

        # Manage buttons
        self._manage_buttons()

        # Will only start when start button is clicked
        self.listen_thread = None

    def _manage_buttons(self):
        # GUI buttons should reflect the current status of the app
        if self.client_bl.socket is not None and self.client_bl.socket_is_active():
            self._start_button.config(state=tk.DISABLED)
            self._stop_button.config(state=tk.NORMAL)
            self._login_button.config(state=tk.NORMAL)
        else:
            self._start_button.config(state=tk.NORMAL)
            self._stop_button.config(state=tk.DISABLED)
            self._login_button.config(state=tk.DISABLED)

        # Log that buttons were reversed only if it's not the first time that function is called, and
        # therefore they were
        if self.first:
            self.first = False
        else:
            protocol.logger.info("[CLIENTGUI] - Buttons reversed")

    def on_click_start_gui(self):
        self.client_bl.on_click_start()
        self._manage_buttons()
        protocol.logger.info(f"[CLIENTGUI] - Socket ID: {id(self.client_bl.socket)}") # Compare this ID with ID in other frames
        self.listen_thread = threading.Thread(target=self.listen, daemon=True)
        self.listen_thread.start()

    def on_click_stop_gui(self):
        self.client_bl.on_click_stop()
        self._manage_buttons()

    def on_click_login_gui(self):
        # Get username and password
        self._username = self._username_text.get()
        self._password = self._password_text.get()
        protocol.logger.info(f"[CLIENTGUI] - Username: {self._username}")
        protocol.logger.info(f"[CLIENTGUI] - Password: {self._password}")

        # Make JSON
        user_data = ("LOGIN", self._username, self._password)
        json_data = json.dumps(user_data)
        protocol.logger.info("[CLIENTGUI] - JSON made")

        # Send JSON to server
        self.client_bl.send_data(json_data)

    def on_click_back_gui(self):
        cast(ClientApp, self.master).show_frame(StartFrame)

    def listen(self):
        while True:
            try:
                data = self.client_bl.socket.recv(1024).decode('utf-8')
                # If user logs in or signs up, redirect to main frame
                # Cast exists so IDE (PyCharm) won't needlessly warn "wrong type"
                if data == "LOGIN":
                    cast(ClientApp, self.master).show_frame(MainFrame)
            except OSError:
                # Exists to ignore the exception shown when the client is stopped but socket.recv() is still active
                break


class SignupFrame(tk.Frame):
    def __init__(self, client_bl):
        # Constructors
        super().__init__()
        self.client_bl = client_bl

        # Show background image
        bg_image = Image.open(protocol.bg_path)
        bg_reimage = bg_image.resize((protocol.width, protocol.height))
        self.bg_pimage: PhotoImage = ImageTk.PhotoImage(bg_reimage)
        self.bg_label = tk.Label(self, image=self.bg_pimage)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create labels
        username_label = tk.Label(self, text="Username:", font=protocol.font)
        password_label = tk.Label(self, text="Password:", font=protocol.font)
        email_label = tk.Label(self, text="Email:", font=protocol.font)

        # Create text fields
        self._username_text = tk.Entry(self, width=protocol.text_width, font=protocol.font)
        self._password_text = tk.Entry(self, width=protocol.text_width, font=protocol.font, show='•')
        self._email_text = tk.Entry(self, width=protocol.text_width, font=protocol.font)

        # Create buttons
        self._start_button = tk.Button(self, text="Start", font=protocol.font, command=self.on_click_start_gui)
        self._stop_button = tk.Button(self, text="Stop", font=protocol.font, command=self.on_click_stop_gui)
        self._signup_button = tk.Button(self, text="Sign up", font=protocol.font, command=self.on_click_signup_gui)
        self._back_button = tk.Button(self, text="Back", font=protocol.font, command=self.on_click_back_gui)

        # Place objects
        username_label.place(x=protocol.labels_x, y=20)
        password_label.place(x=protocol.labels_x, y=220)
        email_label.place(x=protocol.labels_x, y=420)
        self._username_text.place(x=protocol.labels_x, y=80)
        self._password_text.place(x=protocol.labels_x, y=280)
        self._email_text.place(x=protocol.labels_x, y=480)
        self._start_button.place(x=protocol.buttons_x, y=80)
        self._stop_button.place(x=protocol.buttons_x, y=230)
        self._signup_button.place(x=protocol.buttons_x, y=380)
        self._back_button.place(x=protocol.buttons_x, y=530)

        # Create username, password and email
        self._username = None
        self._password = None
        self._email = None

        # First, used for manage_buttons()
        self.first = True

        self.listen_thread = None

        # Manage buttons
        self._manage_buttons()

    def on_click_start_gui(self):
        self.client_bl.on_click_start()
        self._manage_buttons()
        protocol.logger.info(f"[CLIENTGUI] - Socket ID: {id(self.client_bl.socket)}") # Compare this ID with ID in other frames
        self.listen_thread = threading.Thread(target=self.listen, daemon=True)
        self.listen_thread.start()

    def on_click_stop_gui(self):
        self.client_bl.on_click_stop()
        self._manage_buttons()

    def on_click_signup_gui(self):
        # Get username and password
        self._username = self._username_text.get()
        self._password = self._password_text.get()
        self._email = self._email_text.get()
        protocol.logger.info(f"[CLIENTGUI] - Username: {self._username}")
        protocol.logger.info(f"[CLIENTGUI] - Password: {self._password}")
        protocol.logger.info(f"[CLIENTGUI] - Email: {self._email}")

        # Make JSON
        user_data = ("SIGNUP", self._username, self._password, self._email)
        json_data = json.dumps(user_data)
        protocol.logger.info("[CLIENTGUI] - JSON made")

        # Send JSON to server
        self.client_bl.send_data(json_data)

    def on_click_back_gui(self):
        cast(ClientApp, self.master).show_frame(StartFrame)

    def _manage_buttons(self):
        # GUI buttons should reflect the current status of the app
        if self.client_bl.socket is not None:
            self._start_button.config(state=tk.DISABLED)
            self._stop_button.config(state=tk.NORMAL)
            self._signup_button.config(state=tk.NORMAL)
        else:
            self._start_button.config(state=tk.NORMAL)
            self._stop_button.config(state=tk.DISABLED)
            self._signup_button.config(state=tk.DISABLED)

        # Log that buttons were reversed only if it's not the first time that function is called, and
        # therefore they were
        if self.first:
            self.first = False
        else:
            protocol.logger.info("[CLIENTGUI] - Buttons reversed")

    def listen(self):
        while True:
            try:
                data = self.client_bl.socket.recv(1024).decode('utf-8')
                # If user logs in or signs up, redirect to main frame
                # Cast exists so IDE (PyCharm) won't needlessly warn "wrong type"
                if data == "SIGNUP":
                    cast(ClientApp, self.master).show_frame(MainFrame)
            except OSError:
                # Exists to ignore the exception shown when the client is stopped but socket.recv() is still active
                break


class MainFrame(tk.Frame):
    def __init__(self, client_bl):
        # Constructors
        super().__init__()
        self.client_bl = client_bl

        # Show background image
        bg_image = Image.open(protocol.bg_path)
        bg_reimage = bg_image.resize((protocol.width, protocol.height))
        self.bg_pimage: PhotoImage = ImageTk.PhotoImage(bg_reimage)
        self.bg_label = tk.Label(self, image=self.bg_pimage)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create and place stop button
        self._stop_button = tk.Button(self, text="Stop", font=protocol.font, command=self.on_click_stop_gui)
        self._stop_button.place(x=protocol.buttons_x, y=230)

        # Create and place back button
        self._back_button = tk.Button(self, text="Back", font=protocol.font, command=self.on_click_back_gui)
        self._back_button.place(x=protocol.buttons_x, y=380)

        # Configure started flag
        self._started: bool = False

    def on_click_stop_gui(self):
        self._stop_button.config(state=tk.DISABLED)
        self.client_bl.on_click_stop()

    def on_click_back_gui(self):
        cast(ClientApp, self.master).show_frame(StartFrame)


class ClientApp(tk.Tk):
    def __init__(self, client_bl):
        # Constructors
        super().__init__()
        self.client_bl = client_bl

        # Show background image
        bg_image = Image.open(protocol.bg_path)
        bg_reimage = bg_image.resize((protocol.width, protocol.height))
        self.bg_pimage: PhotoImage = ImageTk.PhotoImage(bg_reimage)
        self.bg_label = tk.Label(self, image=self.bg_pimage)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # All these should be done here and not in frames
        self.title("Currency Converter - Start Page")
        self.geometry(f"{protocol.width}x{protocol.height}")
        self._current_frame = None
        self.show_frame(StartFrame)
        cast(tk.Frame, self._current_frame).place(relx=0, rely=0, relwidth=1, relheight=1)

    def show_frame(self, frame):
        # Show a new frame
        if self._current_frame is not None: # If previous frame exists, transfer its client_bl
            protocol.logger.info(f"[CLIENTGUI] - Old BL ID: {id(self._current_frame.client_bl)}")
            protocol.logger.info(f"[CLIENTGUI] - Old socket ID: {id(self._current_frame.client_bl.socket)}")

            self._current_frame = frame(self._current_frame.client_bl)
            protocol.logger.info(f"[CLIENTGUI] - New BL ID: {id(self._current_frame.client_bl)}")
            protocol.logger.info(f"[CLIENTGUI] - New socket ID: {id(self._current_frame.client_bl.socket)}")
        else:
            self._current_frame = frame(self.client_bl)
        protocol.logger.info(f"[CLIENTGUI] - {self._current_frame.__class__.__name__} shown")
        self._current_frame.place(relx=0, rely=0, relwidth=1, relheight=1)


if __name__ == "__main__":
    # Run client
    start_client_bl: ClientBL = ClientBL()
    app: ClientApp = ClientApp(start_client_bl)
    app.mainloop()

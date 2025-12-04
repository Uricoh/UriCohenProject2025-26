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
        self._signup_button = tk.Button(self, text="Sign up", font=protocol.font,
                                        command=lambda:cast(ClientApp, self.master).show_frame(SignupFrame))
        self._login_button = tk.Button(self, text="Log in", font=protocol.font,
                                       command=lambda:cast(ClientApp, self.master).show_frame(LoginFrame))

        # Place buttons
        self._signup_button.place(x=protocol.buttons_x, y=80)
        self._login_button.place(x=protocol.buttons_x, y=230)

        # Configure started flag
        self._started: bool = False


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
        self._back_button = tk.Button(self, text="Back", font=protocol.font,
                                      command=lambda:cast(ClientApp, self.master).show_frame(StartFrame))

        # Configure buttons
        if protocol.socket_exists_and_active(self.client_bl.socket):
            protocol.reverse_button(self._start_button)
        else:
            protocol.reverse_many_buttons((self._stop_button, self._login_button))

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

        # Log socket ID if one exists
        if protocol.socket_exists_and_active(self.client_bl.socket):
            protocol.logger.info(f"[CLIENTGUI] - Socket ID: {id(self.client_bl.socket)}") # Compare this ID with ID in other frames

        # Will only start when start button is clicked
        self.listen_thread = None

    def on_click_start_gui(self):
        self.client_bl.on_click_start()
        cast(ClientApp, self.master).start_listening()
        protocol.reverse_many_buttons((self._start_button, self._stop_button, self._login_button))
        protocol.logger.info(f"[CLIENTGUI] - Socket ID: {id(self.client_bl.socket)}") # Compare this ID with ID in other frames

    def on_click_stop_gui(self):
        self.client_bl.on_click_stop()
        protocol.reverse_many_buttons((self._start_button, self._stop_button, self._login_button))

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
        self._back_button = tk.Button(self, text="Back", font=protocol.font,
                                      command=lambda:cast(ClientApp, self.master).show_frame(StartFrame))

        # Adjust buttons
        if protocol.socket_exists_and_active(self.client_bl.socket):
            protocol.reverse_button(self._start_button)
        else:
            protocol.reverse_many_buttons((self._stop_button, self._signup_button))

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

    def on_click_start_gui(self):
        self.client_bl.on_click_start()
        cast(ClientApp, self.master).start_listening()
        protocol.reverse_many_buttons((self._start_button, self._stop_button, self._signup_button))
        protocol.logger.info(f"[CLIENTGUI] - Socket ID: {id(self.client_bl.socket)}") # Compare this ID with ID in other frames

    def on_click_stop_gui(self):
        self.client_bl.on_click_stop()
        protocol.reverse_many_buttons((self._start_button, self._stop_button, self._signup_button))

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
        self._back_button = tk.Button(self, text="Back", font=protocol.font,
                                      command=lambda:cast(ClientApp, self.master).show_frame(StartFrame))
        self._back_button.place(x=protocol.buttons_x, y=380)

        # Configure started flag
        self._started: bool = False

    def on_click_stop_gui(self):
        protocol.reverse_button(self._stop_button)
        self.client_bl.on_click_stop()


class ClientApp(tk.Tk):
    def __init__(self, client_bl):
        # Constructors
        super().__init__()
        self.client_bl = client_bl

        # Listening flag is used on start_listening() to check if the app is already listening,
        # with client socket created elsewhere on ClientGUI
        self.listening = False

        # Create thread
        self.listen_thread = None

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

    def start_listening(self):
        # If the app already listens, no need to listen again
        if not self.listening:
            threading.Thread(target=self.listen, daemon=True).start()
            self.listening = True

    def listen(self):
        try:
            while protocol.socket_exists_and_active(self.client_bl.socket):
                data = self.client_bl.socket.recv(1024).decode(protocol.json_format)
                if data == "LOGIN" or data == "SIGNUP":
                    self.show_frame(MainFrame)
        except protocol.errors:
            # Exists to revert listening flag and to ignore errors that show up when the client socket closes
            self.listening = False
            pass

    def show_frame(self, frame):
        if self._current_frame is not None:
            self._current_frame.destroy()
        self._current_frame = frame(self.client_bl) # Frame() calls the constructor of any frame (frame class)
        protocol.logger.info(f"[CLIENTGUI] - {self._current_frame.__class__.__name__} shown")
        self._current_frame.place(relx=0, rely=0, relwidth=1, relheight=1)


if __name__ == "__main__":
    # Run client
    start_client_bl: ClientBL = ClientBL()
    app: ClientApp = ClientApp(start_client_bl)
    app.mainloop()

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
        # Constructors and title
        super().__init__()
        self.client_bl = client_bl
        cast(ClientApp, self.master).title("Currency Converter - Start Page")

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

        # Log socket ID if one exists
        if protocol.socket_alive(self.client_bl.socket):
            protocol.logger.info(f"[CLIENTGUI] - Socket ID: {id(self.client_bl.socket)}")
            # Compare this ID with ID in other frames


class LoginFrame(tk.Frame):
    def __init__(self, client_bl):
        # Constructors and title
        super().__init__()
        self.client_bl = client_bl
        cast(ClientApp, self.master).title("Currency Converter - Log in")

        # Show background image
        bg_image = Image.open(protocol.bg_path)
        bg_reimage = bg_image.resize((protocol.width, protocol.height))
        self.bg_pimage: PhotoImage = ImageTk.PhotoImage(bg_reimage)
        self.bg_label = tk.Label(self, image=self.bg_pimage)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create labels
        username_label = tk.Label(self, text="Username:", font=protocol.font)
        password_label = tk.Label(self, text="Password:", font=protocol.font)
        self._fail_label = tk.Label(self, text="Username or password is incorrect", font=protocol.font, fg='red')

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
        if protocol.socket_alive(self.client_bl.socket):
            protocol.reverse_button(self._start_button)
        else:
            protocol.reverse_many_buttons((self._stop_button, self._login_button))

        # Place objects
        username_label.place(x=protocol.labels_x, y=20)
        password_label.place(x=protocol.labels_x, y=220)
        self.show_fail()
        self.hide_fail()
        self._username_text.place(x=protocol.labels_x, y=80)
        self._password_text.place(x=protocol.labels_x, y=280)
        self._start_button.place(x=protocol.buttons_x, y=80)
        self._stop_button.place(x=protocol.buttons_x, y=230)
        self._login_button.place(x=protocol.buttons_x, y=380)
        self._back_button.place(x=protocol.buttons_x, y=530)

        # Log socket ID if one exists
        if protocol.socket_alive(self.client_bl.socket):
            protocol.logger.info(f"[CLIENTGUI] - Socket ID: {id(self.client_bl.socket)}")
            # Compare this ID with ID in other frames

    def on_click_start_gui(self):
        self.client_bl.on_click_start()
        cast(ClientApp, self.master).start_listening()
        protocol.reverse_many_buttons((self._start_button, self._stop_button, self._login_button))
        protocol.logger.info(f"[CLIENTGUI] - Socket ID: {id(self.client_bl.socket)}")
        # Compare this ID with ID in other frames

    def on_click_stop_gui(self):
        self.client_bl.on_click_stop()
        protocol.reverse_many_buttons((self._start_button, self._stop_button, self._login_button))

    def on_click_login_gui(self):
        protocol.logger.info(f"[CLIENTGUI] - Username: {self._username_text.get()}")
        protocol.logger.info(f"[CLIENTGUI] - Password: {self._password_text.get()}")

        # Make JSON
        user_data = ("LOGIN", self._username_text.get(), protocol.get_hash(self._password_text.get()))
        json_data = json.dumps(user_data)
        protocol.logger.info("[CLIENTGUI] - JSON made")

        # Send JSON to server
        self.client_bl.send_data(json_data)

    def show_fail(self):
        self._fail_label.place(x=protocol.labels_x, y=370)

    def hide_fail(self):
        self._fail_label.place_forget()


class SignupFrame(tk.Frame):
    def __init__(self, client_bl):
        # Constructors and title
        super().__init__()
        self.client_bl = client_bl
        cast(ClientApp, self.master).title("Currency Converter - Sign up")

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
        self._fail_label = tk.Label(self, text="Username already exists", font=protocol.font, fg='red')

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
        if protocol.socket_alive(self.client_bl.socket):
            protocol.reverse_button(self._start_button)
        else:
            protocol.reverse_many_buttons((self._stop_button, self._signup_button))

        # Place objects
        username_label.place(x=protocol.labels_x, y=20)
        password_label.place(x=protocol.labels_x, y=220)
        self.show_fail()
        self.hide_fail()
        email_label.place(x=protocol.labels_x, y=420)
        self._username_text.place(x=protocol.labels_x, y=80)
        self._password_text.place(x=protocol.labels_x, y=280)
        self._email_text.place(x=protocol.labels_x, y=480)
        self._start_button.place(x=protocol.buttons_x, y=80)
        self._stop_button.place(x=protocol.buttons_x, y=230)
        self._signup_button.place(x=protocol.buttons_x, y=380)
        self._back_button.place(x=protocol.buttons_x, y=530)

        # Log socket ID if one exists
        if protocol.socket_alive(self.client_bl.socket):
            protocol.logger.info(f"[CLIENTGUI] - Socket ID: {id(self.client_bl.socket)}")
            # Compare this ID with ID in other frames

    def on_click_start_gui(self):
        self.client_bl.on_click_start()
        cast(ClientApp, self.master).start_listening()
        protocol.reverse_many_buttons((self._start_button, self._stop_button, self._signup_button))
        protocol.logger.info(f"[CLIENTGUI] - Socket ID: {id(self.client_bl.socket)}")
        # Compare this ID with ID in other frames

    def on_click_stop_gui(self):
        self.client_bl.on_click_stop()
        protocol.reverse_many_buttons((self._start_button, self._stop_button, self._signup_button))

    def on_click_signup_gui(self):
        protocol.logger.info(f"[CLIENTGUI] - Username: {self._username_text.get()}")
        protocol.logger.info(f"[CLIENTGUI] - Password: {self._password_text.get()}")
        protocol.logger.info(f"[CLIENTGUI] - Email: {self._email_text.get()}")

        # Make JSON
        user_data = ("SIGNUP", self._username_text.get(), protocol.get_hash(self._password_text.get()),
                     self._email_text.get())
        json_data = json.dumps(user_data)
        protocol.logger.info("[CLIENTGUI] - JSON made")

        # Send JSON to server
        self.client_bl.send_data(json_data)

    def show_fail(self):
        self._fail_label.place(x=protocol.labels_x, y=570)

    def hide_fail(self):
        self._fail_label.place_forget()


class MainFrame(tk.Frame):
    def __init__(self, client_bl):
        # Constructors and title
        super().__init__()
        self.client_bl = client_bl
        cast(ClientApp, self.master).title("Currency Converter - Main Page")

        # Show background image
        bg_image = Image.open(protocol.bg_path)
        bg_reimage = bg_image.resize((protocol.width, protocol.height))
        self.bg_pimage: PhotoImage = ImageTk.PhotoImage(bg_reimage)
        self.bg_label = tk.Label(self, image=self.bg_pimage)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create objects
        self._stop_button = tk.Button(self, text="Stop", font=protocol.font, command=self.on_click_stop_gui)
        self._back_button = tk.Button(self, text="Back", font=protocol.font,
                                      command=lambda:cast(ClientApp, self.master).show_frame(StartFrame))
        self._convert_button = tk.Button(self, text="Convert!", font=protocol.font, command=self.on_click_convert_gui)
        self._convert_from = tk.Label(self, text="Convert from", font=protocol.font)
        self._convert_to = tk.Label(self, text="To", font=protocol.font)
        self._amount = tk.Label(self, text="Amount", font=protocol.font)
        self.result_label = tk.Label(self, text="", font=(protocol.font_name, int(1.5 * protocol.font_size)), fg='#27742C')
        self.show_result("")
        self.hide_result()
        self.from_text = tk.Entry(self, width=protocol.currency_width, font=protocol.font)
        self.to_text = tk.Entry(self, width=protocol.currency_width, font=protocol.font)
        self.amount_text = tk.Entry(self, width=int(protocol.text_width / 2), font=protocol.font)

        # Place objects
        self._stop_button.place(x=protocol.buttons_x, y=155)
        self._back_button.place(x=protocol.buttons_x, y=305)
        self._convert_button.place(x=protocol.buttons_x, y=455)
        self._convert_from.place(x=protocol.labels_x, y=20)
        self._convert_to.place(x=protocol.labels_x, y=220)
        self._amount.place(x=protocol.labels_x, y=420)
        self.from_text.place(x=protocol.labels_x, y=80)
        self.to_text.place(x=protocol.labels_x, y=280)
        self.amount_text.place(x=protocol.labels_x, y=480)

        # Log socket ID if one exists
        if protocol.socket_alive(self.client_bl.socket):
            protocol.logger.info(f"[CLIENTGUI] - Socket ID: {id(self.client_bl.socket)}")
            # Compare this ID with ID in other frames

    def on_click_stop_gui(self):
        protocol.reverse_button(self._stop_button)
        self.client_bl.on_click_stop()

    def on_click_convert_gui(self):
        protocol.logger.info("[CLIENTGUI] - Conversion process started")
        protocol.logger.info(f"[CLIENTGUI] - From {self.from_text.get()}")
        protocol.logger.info(f"[CLIENTGUI] - To {self.to_text.get()}")
        protocol.logger.info(f"[CLIENTGUI] - Amount: {self.amount_text.get()}")

        # Make JSON
        convert_info = ("CONVERT", self.from_text.get(), self.to_text.get(), self.amount_text.get())
        json_info = json.dumps(convert_info)
        protocol.logger.info("[CLIENTGUI] - JSON made")

        # Send JSON to server
        self.client_bl.send_data(json_info)

    def show_result(self, text: str):
        self.result_label.config(text=text)
        self.result_label.place(x=450,y=300)

    def hide_result(self):
        self.result_label.place_forget()


class ClientApp(tk.Tk):
    def __init__(self, client_bl):
        # Constructors
        super().__init__()
        self.client_bl = client_bl

        # Listening flag is used on start_listening() to check if the app is already listening,
        # with client socket created elsewhere on ClientGUI
        self.listening = False

        # Show background image
        bg_image = Image.open(protocol.bg_path)
        bg_reimage = bg_image.resize((protocol.width, protocol.height))
        self.bg_pimage: PhotoImage = ImageTk.PhotoImage(bg_reimage)
        self.bg_label = tk.Label(self, image=self.bg_pimage)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # All these should be done here and not in frames
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
            while True:
                data = self.client_bl.socket.recv(1024).decode(protocol.json_format)
                if data == "SIGNUP":
                    protocol.logger.info("[CLIENTGUI] - Signup successful")
                    self.show_frame(MainFrame)
                elif data == "LOGIN":
                    protocol.logger.info("[CLIENTGUI] - Login successful")
                    self.show_frame(MainFrame)
                elif data == "SIGNUPFAIL":
                    protocol.logger.info("[CLIENTGUI] - Signup failed")
                    self._current_frame.show_fail()
                elif data == "LOGINFAIL":
                    protocol.logger.info("[CLIENTGUI] - Login failed")
                    self._current_frame.show_fail()
                elif '=' in data:
                    protocol.logger.info("[CLIENTGUI] - Result message received")
                    self._current_frame.show_result(data)

        except OSError:
            # Exists to revert listening flag and to ignore errors that show up when the client socket closes
            self.listening = False

    def show_frame(self, frame):
        if self._current_frame is not None:
            self._current_frame.destroy()
        self._current_frame = frame(self.client_bl) # Frame() calls the constructor of any frame (frame class)
        self._current_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        protocol.logger.info(f"[CLIENTGUI] - {self._current_frame.__class__.__name__} to show")


if __name__ == "__main__":
    # Run client
    client_bl: ClientBL = ClientBL()
    app: ClientApp = ClientApp(client_bl)
    app.mainloop()

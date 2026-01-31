# Imports
from abc import ABC, abstractmethod
from threading import Thread
from ClientBL import ClientBL
import protocol
from protocol import log
import json
import tkinter as tk
from PIL import Image, ImageTk
from typing import cast

class AppFrame(tk.Frame, ABC): # Frame template for the frames, they should inherit from here
    def __init__(self, client_bl, title: str):
        # Call constructor and get BL
        super().__init__()
        self.client_bl = client_bl

        # Next line exists so IDE (PyCharm) knows the type of self.master and won't show error when using its methods
        self.app_master: ClientApp = cast(ClientApp, self.master)
        self.app_master.title(f"{protocol.APP_NAME} - {title}")

        # Show background image
        bg_image = Image.open(protocol.BG_PATH)
        bg_reimage = bg_image.resize(protocol.SCREEN_AREA)
        self._bg_pimage: tk.PhotoImage = ImageTk.PhotoImage(bg_reimage)
        self._bg_label = tk.Label(self, image=self._bg_pimage)
        self._bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Log socket ID if one exists
        if protocol.socket_alive(self.client_bl.socket):
            log(f"Socket ID: {id(self.client_bl.socket)}")
            # Compare this ID with ID in other frames

    @abstractmethod
    def _place_objects(self):
        pass # This method must be implemented by every frame individually

class StartFrame(AppFrame):
    def __init__(self, client_bl):
        # Constructor
        super().__init__(client_bl, "Start Page")

        # Create buttons
        self._signup_button = tk.Button(self, text="Sign up", font=protocol.FONT,
                                        command=lambda:self.app_master.show_frame(SignupFrame))
        self._login_button = tk.Button(self, text="Log in", font=protocol.FONT,
                                       command=lambda:self.app_master.show_frame(LoginFrame))
        self._guest_button = tk.Button(self, text="Guest mode", font=protocol.FONT, command=self.on_click_guest)

        # Create socket if it doesn't already exist
        if not protocol.socket_alive(self.client_bl.socket):
            self.client_bl.on_open()
            Thread(target=self.app_master.listen, daemon=True).start()
            log(f"Socket ID: {id(self.client_bl.socket)}")

        self._place_objects()

    def _place_objects(self):
        self._signup_button.place(x=protocol.BUTTONS_X, y=80)
        self._login_button.place(x=protocol.BUTTONS_X, y=230)
        self._guest_button.place(x=protocol.BUTTONS_X, y=380)

    def on_click_guest(self):
        self.app_master.username = "Guest"
        self.app_master.show_frame(MainFrame)

class LoginFrame(AppFrame):
    def __init__(self, client_bl):
        # Constructor
        super().__init__(client_bl, "Log in")

        # Create labels
        self._username_label = tk.Label(self, text="Username:", font=protocol.FONT)
        self._password_label = tk.Label(self, text="Password:", font=protocol.FONT)
        self._fail_label = tk.Label(self, text="Username or password is incorrect", font=protocol.FONT, fg='red')

        # Create text fields
        self._username_text = tk.Entry(self, width=protocol.TEXT_WIDTH, font=protocol.FONT)
        self._password_text = tk.Entry(self, width=protocol.TEXT_WIDTH, font=protocol.FONT, show='•')

        # Create buttons
        self._login_button = tk.Button(self, text="Log in", font=protocol.FONT, command=self._on_click_login)
        self._back_button = tk.Button(self, text="Back", font=protocol.FONT,
                                      command=lambda:self.app_master.show_frame(StartFrame))
        self._forgot_button = tk.Button(self, text="Forgot password?", font=protocol.FONT,
                                        command=lambda:self.app_master.show_frame(ForgotEmailFrame))

        self._place_objects()

    def _place_objects(self):
        self._username_label.place(x=protocol.LABELS_X, y=20)
        self._password_label.place(x=protocol.LABELS_X, y=220)
        self.show_fail()
        self.hide_fail()
        self._username_text.place(x=protocol.LABELS_X, y=80)
        self._password_text.place(x=protocol.LABELS_X, y=280)
        # The forgot password button is intentionally placed with the labels, rather than with the buttons
        self._forgot_button.place(x=protocol.LABELS_X, y=420)
        self._login_button.place(x=protocol.BUTTONS_X, y=80)
        self._back_button.place(x=protocol.BUTTONS_X, y=230)

    def _on_click_login(self):
        # Save username
        self.app_master.username = self._username_text.get()

        # Log text field values
        log(f"Username: {self._username_text.get()}")
        log(f"Password: {self._password_text.get()}")

        # Make JSON
        user_data = ("LOGIN", self._username_text.get(), protocol.get_hash(self._password_text.get()))
        json_data = json.dumps(user_data)
        log("JSON made")

        # Send JSON to server
        self.client_bl.send_data(json_data)

    def show_fail(self):
        self._fail_label.place(x=protocol.LABELS_X, y=580)

    def hide_fail(self):
        self._fail_label.place_forget()


class SignupFrame(AppFrame):
    def __init__(self, client_bl):
        # Constructor
        super().__init__(client_bl, "Sign up")

        # Create labels
        self._username_label = tk.Label(self, text="Username:", font=protocol.FONT)
        self._password_label = tk.Label(self, text="Password:", font=protocol.FONT)
        self._email_label = tk.Label(self, text="Email:", font=protocol.FONT)
        self._fail_label = tk.Label(self, text="Username already exists", font=protocol.FONT, fg='red')

        # Create text fields
        self._username_text = tk.Entry(self, width=protocol.TEXT_WIDTH, font=protocol.FONT)
        self._password_text = tk.Entry(self, width=protocol.TEXT_WIDTH, font=protocol.FONT, show='•')
        self._email_text = tk.Entry(self, width=protocol.TEXT_WIDTH, font=protocol.FONT)

        # Create buttons
        self._signup_button = tk.Button(self, text="Sign up", font=protocol.FONT, command=self._on_click_signup)
        self._back_button = tk.Button(self, text="Back", font=protocol.FONT,
                                      command=lambda:self.app_master.show_frame(StartFrame))

        self._place_objects()

    def _place_objects(self):
        self._username_label.place(x=protocol.LABELS_X, y=20)
        self._password_label.place(x=protocol.LABELS_X, y=220)
        self.show_fail()
        self.hide_fail()
        self._email_label.place(x=protocol.LABELS_X, y=420)
        self._username_text.place(x=protocol.LABELS_X, y=80)
        self._password_text.place(x=protocol.LABELS_X, y=280)
        self._email_text.place(x=protocol.LABELS_X, y=480)
        self._signup_button.place(x=protocol.BUTTONS_X, y=80)
        self._back_button.place(x=protocol.BUTTONS_X, y=230)

    def _on_click_signup(self):
        # Save username
        self.app_master.username = self._username_text.get()

        # Log text field values
        log(f"Username: {self._username_text.get()}")
        log(f"Password: {self._password_text.get()}")
        log(f"Email: {self._email_text.get()}")

        # Make JSON
        user_data = ("SIGNUP", self._username_text.get(), protocol.get_hash(self._password_text.get()),
                     self._email_text.get())
        json_data = json.dumps(user_data)
        log("JSON made")

        # Send JSON to server
        self.client_bl.send_data(json_data)

    def show_fail(self):
        self._fail_label.place(x=protocol.LABELS_X, y=600)

    def hide_fail(self):
        self._fail_label.place_forget()


class ForgotEmailFrame(AppFrame):
    def __init__(self, client_bl):
        # Constructor
        super().__init__(client_bl, "Forgot password?")

        # Create objects
        self._not_found_label = tk.Label(self, text="Account not found", font=protocol.FONT, fg='red')
        self._enter_label = tk.Label(self, text="Enter email", font=protocol.FONT)
        self._email_text = tk.Entry(self, width=int(protocol.TEXT_WIDTH * 1.5), font=protocol.FONT)
        self._enter_button = tk.Button(self, text="Enter", font=protocol.FONT, command=self._on_click_enter)
        self._back_button = tk.Button(self, text="Back", font=protocol.FONT,
                                      command=lambda:self.app_master.show_frame(StartFrame))

        self._place_objects()

    def _place_objects(self):
        self.show_not_found()
        self.hide_not_found()
        self._enter_label.place(x=450, y=protocol.CENTER_Y - 100)
        self._email_text.place(x=250, y=protocol.CENTER_Y)
        self._enter_button.place(x=450, y=protocol.CENTER_Y + 100)
        self._back_button.place(x=450, y=protocol.CENTER_Y + 250)

    def _on_click_enter(self):
        log(f"Email: {self._email_text.get()}")

        # Make JSON
        data = ("FORGOTEMAIL", self._email_text.get())
        json_data = json.dumps(data)

        # Send JSON to server
        self.client_bl.send_data(json_data)

    def show_not_found(self):
        self._not_found_label.place(x=450, y=protocol.CENTER_Y - 200)

    def hide_not_found(self):
        self._not_found_label.place_forget()


class ForgotCodeFrame(AppFrame):
    def __init__(self, client_bl):
        # Constructor
        super().__init__(client_bl, "Forgot password?")

        # Create objects
        self._wrong_label = tk.Label(self, text="Wrong code", font=protocol.FONT, fg='red')
        self._enter_label = tk.Label(self, text="Enter code", font=protocol.FONT)
        self._code_text = tk.Entry(self, width=int(protocol.TEXT_WIDTH * 1.5), font=protocol.FONT)
        self._enter_button = tk.Button(self, text="Enter", font=protocol.FONT, command=self.on_click_enter)
        self._back_button = tk.Button(self, text="Back", font=protocol.FONT,
                                      command=lambda:self.app_master.show_frame(StartFrame))

        self._place_objects()

    def _place_objects(self):
        self.show_wrong()
        self.hide_wrong()
        self._enter_label.place(x=450, y=protocol.CENTER_Y - 100)
        self._code_text.place(x=250, y=protocol.CENTER_Y)
        self._enter_button.place(x=450, y=protocol.CENTER_Y + 100)
        self._back_button.place(x=450, y=protocol.CENTER_Y + 250)

    def on_click_enter(self):
        log(f"Code: {self._code_text.get()}")

        # Make JSON
        data = ("FORGOTCODE", self._code_text.get())
        json_data = json.dumps(data)

        # Send JSON to server
        self.client_bl.send_data(json_data)

    def show_wrong(self):
        self._wrong_label.place(x=450, y=protocol.CENTER_Y - 200)

    def hide_wrong(self):
        self._wrong_label.place_forget()


class ForgotSetFrame(AppFrame):
    def __init__(self, client_bl):
        # Constructor
        super().__init__(client_bl, "Forgot password?")

        # Create objects
        self._password_label = tk.Label(self, text="Enter new password", font=protocol.FONT)
        self._password_text = tk.Entry(self, width=protocol.TEXT_WIDTH, font=protocol.FONT, show='•')
        self._password_button = tk.Button(self, text="Enter", font=protocol.FONT, command=self.on_click_enter)

        self._place_objects()

    def _place_objects(self):
        self._password_label.place(x=450, y=protocol.CENTER_Y - 100)
        self._password_text.place(x=450, y=protocol.CENTER_Y)
        self._password_button.place(x=450, y=protocol.CENTER_Y + 100)

    def on_click_enter(self):
        # Make JSON
        data = ("FORGOTSETPASSWORD", protocol.get_hash(self._password_text.get()))
        json_data = json.dumps(data)

        # Send JSON to server
        self.client_bl.send_data(json_data)


class MainFrame(AppFrame):
    def __init__(self, client_bl):
        # Constructor
        super().__init__(client_bl, "Main Page")

        # Create objects
        self._back_button = tk.Button(self, text="Back", font=protocol.FONT,
                                      command=lambda:self.app_master.show_frame(StartFrame))
        self._convert_button = tk.Button(self, text="Convert!", font=protocol.FONT, command=self.on_click_convert)
        self._convert_from = tk.Label(self, text="Convert from", font=protocol.FONT)
        self._convert_to = tk.Label(self, text="To", font=protocol.FONT)
        self._amount = tk.Label(self, text="Amount", font=protocol.FONT)
        self._hello_label = tk.Label(self, text=f"Hello, {self.app_master.username}", font=protocol.FONT, fg='#008000')
        self._result_label = tk.Label(self, text="", font=(protocol.FONT_NAME, int(1.5 * protocol.FONT_SIZE)),
                                      fg='#27742C')
        self.show_result("")
        self.hide_result()
        self._from_text = tk.Entry(self, width=protocol.CURRENCY_WIDTH, font=protocol.FONT)
        self._to_text = tk.Entry(self, width=protocol.CURRENCY_WIDTH, font=protocol.FONT)
        self._amount_text = tk.Entry(self, width=int(protocol.TEXT_WIDTH / 2), font=protocol.FONT)

        self._place_objects()

    def _place_objects(self):
        self._hello_label.place(x=520, y=20)
        self._back_button.place(x=protocol.BUTTONS_X, y=155)
        self._convert_button.place(x=protocol.BUTTONS_X, y=305)
        self._convert_from.place(x=protocol.LABELS_X, y=20)
        self._convert_to.place(x=protocol.LABELS_X, y=220)
        self._amount.place(x=protocol.LABELS_X, y=420)
        self._from_text.place(x=protocol.LABELS_X, y=80)
        self._to_text.place(x=protocol.LABELS_X, y=280)
        self._amount_text.place(x=protocol.LABELS_X, y=480)

    def on_click_convert(self):
        log("Conversion process started")
        log(f"From {self._from_text.get()}")
        log(f"To {self._to_text.get()}")
        log(f"Amount: {self._amount_text.get()}")

        # Make JSON
        convert_info = ("CONVERT", self._from_text.get(), self._to_text.get(), self._amount_text.get())
        json_info = json.dumps(convert_info)
        log("JSON made")

        # Send JSON to server
        self.client_bl.send_data(json_info)

    def show_result(self, result: str):
        self._result_label.config(text=result)
        self._result_label.place(x=350, y=protocol.CENTER_Y)

    def hide_result(self):
        self._result_label.place_forget()


class ClientApp(tk.Tk):
    def __init__(self, client_bl):
        # Constructors
        super().__init__()
        self.client_bl = client_bl

        # Username is needed for hello
        # Username is effectively public so other classes can use it, made possible with public getter and setter
        # Methods, which are both necessary to log changes to variable value
        self._username = None

        # Handle close logic
        # protocol is a tk.Tk method, unrelated to 'protocol' module
        self.protocol("WM_DELETE_WINDOW", self._close_window)

        # All these should be done here and not in frames
        self.geometry(f"{protocol.SCREEN_WIDTH}x{protocol.SCREEN_HEIGHT}")
        self._current_frame = None
        self.show_frame(StartFrame)

    # All of this is necessary in order to automatically log changes to self.username
    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, new_value):
        old_value = self._username
        if old_value is None:
            old_value = "[empty]"

        self._username = new_value
        log(f"Username changed from {old_value} to {new_value}")

    def listen(self):
        try:
            while True:
                # Listen and proceed by instructions from server
                data = self.client_bl.socket.recv(protocol.BUFFER_SIZE).decode(protocol.ENCODE_FORMAT)
                if data == "SIGNUP":
                    log("Signup successful")
                    self.show_frame(MainFrame)
                elif data == "LOGIN":
                    log("Login successful")
                    self.show_frame(MainFrame)
                elif data == "SIGNUPFAIL":
                    log("Signup failed")
                    self._current_frame.show_fail()
                elif data == "LOGINFAIL":
                    log("Login failed")
                    self._current_frame.show_fail()
                elif data == "FORGOTEMAIL": # Forgot password, passed stage 1
                    log("Forgot email successful")
                    self.show_frame(ForgotCodeFrame)
                elif data == "FORGOTEMAILFAIL": # Forgot password, failed stage 1
                    log("Forgot email failed")
                    self._current_frame.show_not_found()
                elif data == "FORGOTCODE": # Forgot password, passed stage 2
                    log("Forgot code successful")
                    self.show_frame(ForgotSetFrame)
                elif data == "FORGOTCODEFAIL": # Forgot password, failed stage 2
                    log("Forgot code failed")
                    self._current_frame.show_wrong()
                elif data == "FORGOTSETPASSWORD": # Forgot password, passed stage 3
                    log("Password reset")
                    self.show_frame(LoginFrame)
                elif '=' in data or data == "Error":
                    log("Result message received")
                    self._current_frame.show_result(data)

        except OSError:
            # Exists to log end of listen and ignore errors that show up when the client socket closes
            log("Stopped listening")
            pass

    def show_frame(self, frame):
        if self._current_frame is not None:
            self._current_frame.destroy()
        self._current_frame = frame(self.client_bl) # frame() calls the constructor of any frame (frame class)
        self._current_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        log(f"{self._current_frame.__class__.__name__} to show")

    def _close_window(self):
        log("Client is shutting down")
        self.client_bl.on_close()
        self.destroy() # Has to be included in order to actually close the window


if __name__ == "__main__":
    # Run client
    client_bl: ClientBL = ClientBL()
    app: ClientApp = ClientApp(client_bl)
    app.mainloop()

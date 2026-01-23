# Imports
from abc import ABC
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
        self.bg_pimage: tk.PhotoImage = ImageTk.PhotoImage(bg_reimage)
        self.bg_label = tk.Label(self, image=self.bg_pimage)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Log socket ID if one exists
        if protocol.socket_alive(self.client_bl.socket):
            log(f"Socket ID: {id(self.client_bl.socket)}")
            # Compare this ID with ID in other frames

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

        # Place buttons
        self._signup_button.place(x=protocol.BUTTONS_X, y=80)
        self._login_button.place(x=protocol.BUTTONS_X, y=230)
        self._guest_button.place(x=protocol.BUTTONS_X, y=380)

        # Create socket if it doesn't already exist
        if not protocol.socket_alive(self.client_bl.socket):
            self.client_bl.on_open()
            Thread(target=self.app_master.listen, daemon=True).start()
            log(f"Socket ID: {id(self.client_bl.socket)}")

    def on_click_guest(self):
        self.app_master.set_username("Guest")
        self.app_master.show_frame(MainFrame)

class LoginFrame(AppFrame):
    def __init__(self, client_bl):
        # Constructor
        super().__init__(client_bl, "Log in")

        # Create labels
        username_label = tk.Label(self, text="Username:", font=protocol.FONT)
        password_label = tk.Label(self, text="Password:", font=protocol.FONT)
        self._fail_label = tk.Label(self, text="Username or password is incorrect", font=protocol.FONT, fg='red')

        # Create text fields
        self._username_text = tk.Entry(self, width=protocol.TEXT_WIDTH, font=protocol.FONT)
        self._password_text = tk.Entry(self, width=protocol.TEXT_WIDTH, font=protocol.FONT, show='•')

        # Create buttons
        self._login_button = tk.Button(self, text="Log in", font=protocol.FONT, command=self.on_click_login)
        self._back_button = tk.Button(self, text="Back", font=protocol.FONT,
                                      command=lambda:self.app_master.show_frame(StartFrame))
        self._forgot_button = tk.Button(self, text="Forgot password?", font=protocol.FONT,
                                        command=lambda:self.app_master.show_frame(ForgotEmailFrame))

        # Place objects
        username_label.place(x=protocol.LABELS_X, y=20)
        password_label.place(x=protocol.LABELS_X, y=220)
        self.show_fail()
        self.hide_fail()
        self._username_text.place(x=protocol.LABELS_X, y=80)
        self._password_text.place(x=protocol.LABELS_X, y=280)
        self._forgot_button.place(x=protocol.LABELS_X, y=420)
        # The forgot password button is intentionally placed with the labels, rather than with the buttons
        self._login_button.place(x=protocol.BUTTONS_X, y=80)
        self._back_button.place(x=protocol.BUTTONS_X, y=230)

    def on_click_login(self):
        log(f"Username: {self._username_text.get()}")
        log(f"Password: {self._password_text.get()}")

        # Save username
        self.app_master.set_username(self._username_text.get())

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
        username_label = tk.Label(self, text="Username:", font=protocol.FONT)
        password_label = tk.Label(self, text="Password:", font=protocol.FONT)
        email_label = tk.Label(self, text="Email:", font=protocol.FONT)
        self._fail_label = tk.Label(self, text="Username already exists", font=protocol.FONT, fg='red')

        # Create text fields
        self._username_text = tk.Entry(self, width=protocol.TEXT_WIDTH, font=protocol.FONT)
        self._password_text = tk.Entry(self, width=protocol.TEXT_WIDTH, font=protocol.FONT, show='•')
        self._email_text = tk.Entry(self, width=protocol.TEXT_WIDTH, font=protocol.FONT)

        # Create buttons
        self._signup_button = tk.Button(self, text="Sign up", font=protocol.FONT, command=self.on_click_signup)
        self._back_button = tk.Button(self, text="Back", font=protocol.FONT,
                                      command=lambda:self.app_master.show_frame(StartFrame))

        # Place objects
        username_label.place(x=protocol.LABELS_X, y=20)
        password_label.place(x=protocol.LABELS_X, y=220)
        self.show_fail()
        self.hide_fail()
        email_label.place(x=protocol.LABELS_X, y=420)
        self._username_text.place(x=protocol.LABELS_X, y=80)
        self._password_text.place(x=protocol.LABELS_X, y=280)
        self._email_text.place(x=protocol.LABELS_X, y=480)
        self._signup_button.place(x=protocol.BUTTONS_X, y=80)
        self._back_button.place(x=protocol.BUTTONS_X, y=230)

    def on_click_signup(self):
        log(f"Username: {self._username_text.get()}")
        log(f"Password: {self._password_text.get()}")
        log(f"Email: {self._email_text.get()}")

        # Save username
        self.app_master.set_username(self._username_text.get())

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
        self.not_found_label = tk.Label(self, text="Account not found", font=protocol.FONT, fg='red')
        self.enter_label = tk.Label(self, text="Enter email", font=protocol.FONT)
        self.email_text = tk.Entry(self, width=int(protocol.TEXT_WIDTH * 1.5), font=protocol.FONT)
        self.enter_button = tk.Button(self, text="Enter", font=protocol.FONT, command=self.on_click_enter)
        self.back_button = tk.Button(self, text="Back", font=protocol.FONT,
                                     command=lambda:self.app_master.show_frame(StartFrame))

        # Place objects
        self.show_not_found()
        self.hide_not_found()
        self.enter_label.place(x=450, y=protocol.CENTER_Y - 100)
        self.email_text.place(x=250, y=protocol.CENTER_Y)
        self.enter_button.place(x=450, y=protocol.CENTER_Y + 100)
        self.back_button.place(x=450, y=protocol.CENTER_Y + 250)

    def on_click_enter(self):
        log(f"Email: {self.email_text.get()}")

        # Make JSON
        data = ("FORGOTEMAIL", self.email_text.get())
        json_data = json.dumps(data)

        # Send JSON to server
        self.client_bl.send_data(json_data)

    def show_not_found(self):
        self.not_found_label.place(x=450, y=protocol.CENTER_Y - 200)

    def hide_not_found(self):
        self.not_found_label.place_forget()


class ForgotCodeFrame(AppFrame):
    def __init__(self, client_bl):
        # Constructor
        super().__init__(client_bl, "Forgot password?")

        # Create objects
        self.wrong_label = tk.Label(self, text="Wrong code", font=protocol.FONT, fg='red')
        self.enter_label = tk.Label(self, text="Enter code", font=protocol.FONT)
        self.code_text = tk.Entry(self, width=int(protocol.TEXT_WIDTH * 1.5), font=protocol.FONT)
        self.enter_button = tk.Button(self, text="Enter", font=protocol.FONT, command=self.on_click_enter)
        self.back_button = tk.Button(self, text="Back", font=protocol.FONT,
                                     command=lambda:self.app_master.show_frame(StartFrame))

        # Place objects
        self.show_wrong()
        self.hide_wrong()
        self.enter_label.place(x=450, y=protocol.CENTER_Y - 100)
        self.code_text.place(x=250, y=protocol.CENTER_Y)
        self.enter_button.place(x=450, y=protocol.CENTER_Y + 100)
        self.back_button.place(x=450, y=protocol.CENTER_Y + 250)

    def on_click_enter(self):
        log(f"Code: {self.code_text.get()}")

        # Make JSON
        data = ("FORGOTCODE", self.code_text.get())
        json_data = json.dumps(data)

        # Send JSON to server
        self.client_bl.send_data(json_data)

    def show_wrong(self):
        self.wrong_label.place(x=450, y=protocol.CENTER_Y - 200)

    def hide_wrong(self):
        self.wrong_label.place_forget()


class ForgotSetFrame(AppFrame):
    def __init__(self, client_bl):
        # Constructor
        super().__init__(client_bl, "Forgot password?")

        # Create objects
        self.password_label = tk.Label(self, text="Enter new password", font=protocol.FONT)
        self.password_text = tk.Entry(self, width=protocol.TEXT_WIDTH, font=protocol.FONT, show='•')
        self.password_button = tk.Button(self, text="Enter", font=protocol.FONT, command=self.on_click_enter)

        # Place objects
        self.password_label.place(x=450, y=protocol.CENTER_Y - 100)
        self.password_text.place(x=450, y=protocol.CENTER_Y)
        self.password_button.place(x=450, y=protocol.CENTER_Y + 100)

    def on_click_enter(self):
        # Make JSON
        data = ("FORGOTSETPASSWORD", protocol.get_hash(self.password_text.get()))
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
        self.hello_label = tk.Label(self, text=f"Hello, {self.app_master.username}", font=protocol.FONT, fg='#008000')
        self.result_label = tk.Label(self, text="", font=(protocol.FONT_NAME, int(1.5 * protocol.FONT_SIZE)),
                                     fg='#27742C')
        self.show_result("")
        self.hide_result()
        self.from_text = tk.Entry(self, width=protocol.CURRENCY_WIDTH, font=protocol.FONT)
        self.to_text = tk.Entry(self, width=protocol.CURRENCY_WIDTH, font=protocol.FONT)
        self.amount_text = tk.Entry(self, width=int(protocol.TEXT_WIDTH / 2), font=protocol.FONT)

        # Place objects
        self.hello_label.place(x=520, y=20)
        self._back_button.place(x=protocol.BUTTONS_X, y=155)
        self._convert_button.place(x=protocol.BUTTONS_X, y=305)
        self._convert_from.place(x=protocol.LABELS_X, y=20)
        self._convert_to.place(x=protocol.LABELS_X, y=220)
        self._amount.place(x=protocol.LABELS_X, y=420)
        self.from_text.place(x=protocol.LABELS_X, y=80)
        self.to_text.place(x=protocol.LABELS_X, y=280)
        self.amount_text.place(x=protocol.LABELS_X, y=480)

    def on_click_convert(self):
        log("Conversion process started")
        log(f"From {self.from_text.get()}")
        log(f"To {self.to_text.get()}")
        log(f"Amount: {self.amount_text.get()}")

        # Make JSON
        convert_info = ("CONVERT", self.from_text.get(), self.to_text.get(), self.amount_text.get())
        json_info = json.dumps(convert_info)
        log("JSON made")

        # Send JSON to server
        self.client_bl.send_data(json_info)

    def show_result(self, result: str):
        self.result_label.config(text=result)
        self.result_label.place(x=350, y=protocol.CENTER_Y)

    def hide_result(self):
        self.result_label.place_forget()


class ClientApp(tk.Tk):
    def __init__(self, client_bl):
        # Constructors
        super().__init__()
        self.client_bl = client_bl

        # Username is needed for hello
        self.username = None

        # Handle close logic
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        # All these should be done here and not in frames
        self.geometry(f"{protocol.SCREEN_WIDTH}x{protocol.SCREEN_HEIGHT}")
        self._current_frame = None
        self.show_frame(StartFrame)

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
        self._current_frame = frame(self.client_bl) # Frame() calls the constructor of any frame (frame class)
        self._current_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        log(f"{self._current_frame.__class__.__name__} to show")

    def set_username(self, username: str):
        self.username = username
        log(f"Username {self.username} saved")

    def close_window(self):
        log("Client is shutting down")
        self.client_bl.on_close()
        self.destroy() # Has to be included in order to actually close the window


if __name__ == "__main__":
    # Run client
    client_bl: ClientBL = ClientBL()
    app: ClientApp = ClientApp(client_bl)
    app.mainloop()

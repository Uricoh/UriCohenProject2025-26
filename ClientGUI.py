# Imports
from abc import ABC, abstractmethod
from ClientBL import ClientBL
import protocol
from protocol import log
import tkinter as tk
from tkinter import ttk, PhotoImage
from threading import Thread
import json
from typing import cast

class AppFrame(tk.Frame, ABC): # Frame template for the frames, they should inherit from here
    def __init__(self, client_bl, title: str):
        # Call constructor and get BL
        super().__init__()
        self.client_bl = client_bl

        # Next line exists so IDE (PyCharm) knows the type of self.master and won't show error when using its methods
        self.app_master: ClientApp = cast(ClientApp, self.master)
        self.app_master.title(f"{protocol.APP_NAME} - {title}")

        # Log socket ID if one exists
        if protocol.socket_alive(self.client_bl.socket):
            log(f"Socket ID: {id(self.client_bl.socket)}")
            # Compare this ID with ID in other frames

        # Create background image
        self._bg_pimage: PhotoImage = protocol.open_image(protocol.BG_PATH, protocol.SCREEN_AREA)

        # Canvas
        self._canvas = tk.Canvas(self, width=protocol.SCREEN_WIDTH, height=protocol.SCREEN_HEIGHT)
        self._canvas.pack(fill="both", expand=True)
        self._canvas.create_image(0, 0, image=self._bg_pimage, anchor='nw')

    def create_user_text(self, username: str):
        x = protocol.SCREEN_WIDTH - 280
        y = 40
        self._canvas.create_text(x, y, text=f"👤{username}", fill="#c58917", font=protocol.FONT)

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
        self._signup_button.place(x=protocol.RIGHT_X, y=80)
        self._login_button.place(x=protocol.RIGHT_X, y=230)
        self._guest_button.place(x=protocol.RIGHT_X, y=380)

    def on_click_guest(self):
        self.app_master.username = protocol.GUEST_USERNAME
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
        self._username_label.place(x=protocol.LEFT_X, y=20)
        self._password_label.place(x=protocol.LEFT_X, y=220)
        self.show_fail()
        self.hide_fail()
        self._username_text.place(x=protocol.LEFT_X, y=80)
        self._password_text.place(x=protocol.LEFT_X, y=280)

        # The forgot password button is intentionally placed with the labels, rather than with the buttons
        self._forgot_button.place(x=protocol.LEFT_X, y=420)
        self._login_button.place(x=protocol.RIGHT_X, y=80)
        self._back_button.place(x=protocol.RIGHT_X, y=230)

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
        self._fail_label.place(x=protocol.LEFT_X, y=580)

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
        self._username_label.place(x=protocol.LEFT_X, y=20)
        self._password_label.place(x=protocol.LEFT_X, y=220)
        self.show_fail()
        self.hide_fail()
        self._email_label.place(x=protocol.LEFT_X, y=420)
        self._username_text.place(x=protocol.LEFT_X, y=80)
        self._password_text.place(x=protocol.LEFT_X, y=280)
        self._email_text.place(x=protocol.LEFT_X, y=480)
        self._signup_button.place(x=protocol.RIGHT_X, y=80)
        self._back_button.place(x=protocol.RIGHT_X, y=230)

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
        self._fail_label.place(x=protocol.LEFT_X, y=600)

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

        # Create reverse image
        self._switch_pimage: PhotoImage = protocol.open_image(protocol.SWITCH_PATH, (75, 75))

        # Create objects
        self._switch_button = tk.Button(self, image=self._switch_pimage, command=self._on_click_switch)
        self._convert_button = tk.Button(self, text="Convert!", font=protocol.FONT, command=self._on_click_convert)
        protocol.color_button_text(self._convert_button, "#c04000")
        self._history_button = tk.Button(self, text="History", font=protocol.FONT, command=self._on_click_history_gui)
        self._back_button = tk.Button(self, text="Back", font=protocol.FONT,
                                      command=lambda:self.app_master.show_frame(StartFrame))
        self._convert_from = tk.Label(self, text="Convert from", font=protocol.FONT)
        self._convert_to = tk.Label(self, text="To", font=protocol.FONT)
        self._amount = tk.Label(self, text="Amount", font=protocol.FONT)
        self._hello_label = tk.Label(self, text=f"Hello, {self.app_master.username}", font=protocol.FONT, fg='#008000')
        self._result_label = tk.Label(self, text="", font=(protocol.FONT_NAME, int(1.2 * protocol.FONT_SIZE)),
                                      fg='#27742C')
        self.show_result()
        self.hide_result()
        self._from_combobox = ttk.Combobox(self, values=protocol.CURRENCIES,
                                           font=(protocol.FONT_NAME, int(0.75 * protocol.FONT_SIZE)), state="normal")
        self._to_combobox = ttk.Combobox(self, values=protocol.CURRENCIES,
                                         font=(protocol.FONT_NAME, int(0.75 * protocol.FONT_SIZE)), state="normal")
        self._amount_text = tk.Entry(self, width=int(protocol.TEXT_WIDTH / 2),
                                     font=(protocol.FONT_NAME, int(0.75 * protocol.FONT_SIZE)))

        self._place_objects()

    def _place_objects(self):
        self._hello_label.place(x=520, y=20)
        self._switch_button.place(x=340, y=170)
        self._convert_button.place(x=protocol.RIGHT_X, y=155)
        self._history_button.place(x=protocol.RIGHT_X, y=305)
        self._back_button.place(x=protocol.RIGHT_X, y=455)
        self._convert_from.place(x=protocol.LEFT_X, y=20)
        self._convert_to.place(x=protocol.LEFT_X, y=220)
        self._amount.place(x=protocol.LEFT_X, y=420)
        self._from_combobox.place(x=protocol.LEFT_X, y=80)
        self._to_combobox.place(x=protocol.LEFT_X, y=280)
        self._amount_text.place(x=protocol.LEFT_X, y=480)

    def _on_click_switch(self):
        old_from = self._from_combobox.get()
        protocol.put_text_in_button(self._from_combobox, self._to_combobox.get())
        protocol.put_text_in_button(self._to_combobox, old_from)
        log(f"Currencies switched, now {self._from_combobox.get()} to {self._to_combobox.get()}")

    def _on_click_convert(self):
        log("Conversion process started")
        log(f"From {self._from_combobox.get()}")
        log(f"To {self._to_combobox.get()}")
        log(f"Amount: {self._amount_text.get()}")

        convert_info = ("CONVERT", self._from_combobox.get().split()[0], self._to_combobox.get().split()[0],
                        self._amount_text.get())
        json_info = json.dumps(convert_info)
        log("JSON made")

        # Send JSON to server
        self.client_bl.send_data(json_info)

    def _on_click_history_gui(self):
        self.client_bl.send_data("HISTORY")
        self.app_master.show_frame(HistoryFrame)

    def show_result(self, result: str = ""):
        self._result_label.config(text=result)
        self._result_label.place(x=450, y=170)

    def hide_result(self):
        self._result_label.place_forget()


class HistoryFrame(AppFrame):
    def __init__(self, client_bl):
        # Constructor
        super().__init__(client_bl, "History")

        # Create objects
        self._history_label = tk.Label(self, text="History", font=(protocol.FONT_NAME, int(1.75 * protocol.FONT_SIZE)))
        self._back_button = tk.Button(self, text="Back", font=protocol.FONT,
                                      command=lambda:self.app_master.show_frame(MainFrame))

        # Create tree
        try:
            self._tree = protocol.create_table(self.app_master, protocol.HISTORY_TBL_HEADERS,
                                               self.app_master.converts[self.app_master.username])
        except KeyError:
            self._tree = protocol.create_table(self.app_master, protocol.HISTORY_TBL_HEADERS, [])

        self._place_objects()

    def _place_objects(self):
        self._tree.place(x=protocol.LEFT_X, y=200, width=800, height=300)
        self._back_button.place(x=protocol.RIGHT_X, y=455)
        self._history_label.place(x=protocol.LEFT_X, y=int(0.75 * protocol.LEFT_X))


class ClientApp(tk.Tk):
    def __init__(self, client_bl):
        # Constructors
        super().__init__()
        self.client_bl = client_bl

        # Username is needed for hello
        # Username is effectively public so other classes can use it, made possible with public getter and setter
        # Methods, which are both necessary to log changes to variable value
        self._username = protocol.GUEST_USERNAME

        # Convert lists are needed for history frame
        self.converts: dict = {}

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
        self._username = new_value
        log(f"Username changed from {old_value} to {new_value}")

    def listen(self):
        try:
            while True:
                # Listen and proceed by instructions from server
                data: str = self.client_bl.socket.recv(protocol.BUFFER_SIZE).decode(protocol.ENCODE_FORMAT)
                if data.startswith("[") and data.endswith("]") or data.startswith("{") and data.endswith("}"):
                    # Checks if data is a JSON string
                    response_data = json.loads(data)
                    if response_data[0] == "SIGNUP":
                        log("Signup successful")
                        self.converts[self.username] = response_data[1]
                        self.show_frame(MainFrame)
                    elif response_data[0] == "LOGIN":
                        log("Login successful")
                        self.converts[self.username] = response_data[1]
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
                elif '=' in data or data == protocol.ERROR_MSG:
                    try:
                        # This logic only works in current result string, change logic if changing string
                        data_words = data.split()

                        # Log and ignore errors related to conversion error
                        source = data_words[1]
                        dest = data_words[4]
                        amount = data_words[0]
                        result = data_words[3]

                        try: # May raise KeyError because self.converts[self.username] might not exist
                            if len(self.converts[self.username]) == protocol.TBL_CAPACITY:
                                self.converts[self.username].pop(0)
                        except KeyError:
                            pass

                        try:
                            self.converts[self.username].append((source, dest, amount, result))
                        except KeyError:
                            self.converts[self.username] = [(source, dest, amount, result)]

                        log(f"Result message received, source={source}, dest={dest}, amount={amount}, result={result}")

                    except IndexError as e:
                        log(f"Error: {e}")

                    self._current_frame.show_result(data)

        except OSError:
            # Exists to log end of listen and ignore errors that show up when the client socket closes
            log("Stopped listening")

    def show_frame(self, frame):
        if self._current_frame is not None:
            self._current_frame.destroy()

        # frame() calls the constructor of any frame (frame class)
        self._current_frame = frame(self.client_bl)
        self._current_frame.create_user_text(self.username)
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

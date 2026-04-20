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
from io import BytesIO
import base64
from email_validator import validate_email, EmailNotValidError

class AppFrame(tk.Frame, ABC): # Frame template for the frames, they should inherit from here
    def __init__(self, client_bl, title: str):
        # Call constructor and get BL
        super().__init__()
        self.client_bl = client_bl

        # Next line exists so IDE (PyCharm) knows the type of self.master and won't show error when using its methods
        self.app_master: ClientApp = cast(ClientApp, self.master)
        self.app_master.title(f"{protocol.APP_NAME} - {title}")

        # Create background image
        self._bg_pimage: PhotoImage = protocol.open_image(protocol.BG_PATH, protocol.SCREEN_AREA)

        # Create canvas
        self.canvas = tk.Canvas(self, width=protocol.SCREEN_WIDTH, height=protocol.SCREEN_HEIGHT)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self._bg_pimage, anchor='nw')

        # Create user text
        x = int(1.3 * protocol.RIGHT_X)
        y = 40
        self.canvas.create_text(x, y, text=f"👤{self.app_master.username}", fill="#c58917", font=protocol.FONT)

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
        self._username_entry = tk.Entry(self, width=protocol.TEXT_WIDTH, font=protocol.FONT)
        self._password_entry = tk.Entry(self, width=protocol.TEXT_WIDTH, font=protocol.FONT, show='•')

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
        self._username_entry.place(x=protocol.LEFT_X, y=80)
        self._password_entry.place(x=protocol.LEFT_X, y=280)

        # The forgot password button is intentionally placed with the labels, rather than with the buttons
        self._forgot_button.place(x=protocol.LEFT_X, y=420)
        self._login_button.place(x=protocol.RIGHT_X, y=80)
        self._back_button.place(x=protocol.RIGHT_X, y=230)

    def _on_click_login(self):
        # Save username
        self.app_master.username = self._username_entry.get()

        # Log username
        log(f"Username: {self._username_entry.get()}")

        # Make JSON
        user_data = ("LOGIN", self._username_entry.get(), protocol.get_hash(self._password_entry.get()))
        json_data = protocol.make_json(user_data)

        # Send JSON to server
        self.client_bl.send_data(json_data)

    def show_fail(self):
        self._fail_label.place(x=protocol.LEFT_X, y=2 * protocol.CENTER_Y)

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
        self._fail_label = tk.Label(self, text="Check data", font=protocol.FONT, fg='red')

        # Create text fields
        self._username_entry = tk.Entry(self, width=protocol.TEXT_WIDTH, font=protocol.FONT)
        self._password_entry = tk.Entry(self, width=protocol.TEXT_WIDTH, font=protocol.FONT, show='•')
        self._email_entry = tk.Entry(self, width=protocol.TEXT_WIDTH, font=protocol.FONT)

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
        self._username_entry.place(x=protocol.LEFT_X, y=80)
        self._password_entry.place(x=protocol.LEFT_X, y=280)
        self._email_entry.place(x=protocol.LEFT_X, y=480)
        self._signup_button.place(x=protocol.RIGHT_X, y=80)
        self._back_button.place(x=protocol.RIGHT_X, y=230)

    def _on_click_signup(self):
        # Save username
        self.app_master.username = self._username_entry.get()

        # Log text field values
        log(f"Username: {self._username_entry.get()}")
        log(f"Password: {self._password_entry.get()}")
        log(f"Email: {self._email_entry.get()}")

        # Check if password is invalid
        if len(self._password_entry.get()) < protocol.MIN_PASSWORD_LENGTH:
            self.show_fail()

        else:
            # Check for email validity
            try:
                validate_email(self._email_entry.get())

                # Make JSON
                user_data = ("SIGNUP", self._username_entry.get(), protocol.get_hash(self._password_entry.get()),
                             self._email_entry.get())
                json_data = protocol.make_json(user_data)

                # Send JSON to server
                self.client_bl.send_data(json_data)

            except EmailNotValidError:
                self.show_fail()

    def show_fail(self):
        self._fail_label.place(x=protocol.LEFT_X, y=2 * protocol.CENTER_Y)

    def hide_fail(self):
        self._fail_label.place_forget()


class ForgotEmailFrame(AppFrame):
    def __init__(self, client_bl):
        # Constructor
        super().__init__(client_bl, "Forgot password?")

        # Create objects
        self._not_found_label = tk.Label(self, text="Account not found", font=protocol.FONT, fg='red')
        self._email_label = tk.Label(self, text="Enter email", font=protocol.FONT)
        self._email_entry = tk.Entry(self, width=int(1.5 * protocol.TEXT_WIDTH), font=protocol.FONT)
        self._enter_button = tk.Button(self, text="Enter", font=protocol.FONT, command=self._on_click_enter)
        self._back_button = tk.Button(self, text="Back", font=protocol.FONT,
                                      command=lambda:self.app_master.show_frame(LoginFrame))

        self._place_objects()

    def _place_objects(self):
        self.show_not_found()
        self.hide_not_found()
        self._email_label.place(x=450, y=int(0.65 * protocol.CENTER_Y))
        self._email_entry.place(x=250, y=protocol.CENTER_Y)
        self._enter_button.place(x=450, y=int(1.35 * protocol.CENTER_Y))
        self._back_button.place(x=450, y=int(1.85 * protocol.CENTER_Y))

    def _on_click_enter(self):
        log(f"Email: {self._email_entry.get()}")

        # Make JSON
        user_data = ("FORGOTEMAIL", self._email_entry.get())
        json_data = protocol.make_json(user_data)

        # Send JSON to server
        self.client_bl.send_data(json_data)

    def show_not_found(self):
        self._not_found_label.place(x=450, y=int(0.35 * protocol.CENTER_Y))

    def hide_not_found(self):
        self._not_found_label.place_forget()


class ForgotCodeFrame(AppFrame):
    def __init__(self, client_bl):
        # Constructor
        super().__init__(client_bl, "Forgot password?")

        # Create objects
        self._wrong_label = tk.Label(self, text="Wrong code", font=protocol.FONT, fg='red')
        self._code_label = tk.Label(self, text="Enter code", font=protocol.FONT)
        self._code_entry = tk.Entry(self, width=int(1.5 * protocol.TEXT_WIDTH), font=protocol.FONT)
        self._enter_button = tk.Button(self, text="Enter", font=protocol.FONT, command=self.on_click_enter)
        self._back_button = tk.Button(self, text="Back", font=protocol.FONT,
                                      command=lambda:self.app_master.show_frame(LoginFrame))

        self._place_objects()

    def _place_objects(self):
        self.show_wrong()
        self.hide_wrong()
        self._code_label.place(x=450, y=int(0.65 * protocol.CENTER_Y))
        self._code_entry.place(x=250, y=protocol.CENTER_Y)
        self._enter_button.place(x=450, y=int(1.35 * protocol.CENTER_Y))
        self._back_button.place(x=450, y=int(1.85 * protocol.CENTER_Y))

    def on_click_enter(self):
        log(f"Code: {self._code_entry.get()}")

        # Make JSON
        user_data = ("FORGOTCODE", self._code_entry.get())
        json_data = protocol.make_json(user_data)

        # Send JSON to server
        self.client_bl.send_data(json_data)

    def show_wrong(self):
        self._wrong_label.place(x=450, y=int(0.35 * protocol.CENTER_Y))

    def hide_wrong(self):
        self._wrong_label.place_forget()


class ForgotSetFrame(AppFrame):
    def __init__(self, client_bl):
        # Constructor
        super().__init__(client_bl, "Forgot password?")

        # Create objects
        self._password_label = tk.Label(self, text="Enter new password", font=protocol.FONT)
        self._password_entry = tk.Entry(self, width=protocol.TEXT_WIDTH, font=protocol.FONT, show='•')
        self._password_button = tk.Button(self, text="Enter", font=protocol.FONT, command=self.on_click_enter)

        self._place_objects()

    def _place_objects(self):
        self._password_label.place(x=450, y=int(0.65 * protocol.CENTER_Y))
        self._password_entry.place(x=450, y=protocol.CENTER_Y)
        self._password_button.place(x=450, y=int(1.35 * protocol.CENTER_Y))

    def on_click_enter(self):
        # Make JSON
        user_data = ("FORGOTSETPASSWORD", protocol.get_hash(self._password_entry.get()))
        json_data = protocol.make_json(user_data)

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
        self._history_button = tk.Button(self, text="History", font=protocol.FONT,
                                         command=lambda:self.app_master.show_frame(HistoryFrame))
        self._stocks_button = tk.Button(self, text="Stocks", font=protocol.FONT,
                                        command=lambda:self.app_master.show_frame(StocksFrame))
        if self.app_master.username == protocol.GUEST_USERNAME:
            protocol.reverse_button(self._stocks_button)
        self._back_button = tk.Button(self, text="Back", font=protocol.FONT,
                                      command=lambda:self.app_master.show_frame(StartFrame))
        self._convert_from_label = tk.Label(self, text="Convert from", font=protocol.FONT)
        self._convert_to_label = tk.Label(self, text="To", font=protocol.FONT)
        self._amount_label = tk.Label(self, text="Amount", font=protocol.FONT)
        self._hello_label = tk.Label(self, text=f"Hello, {self.app_master.username}", font=protocol.FONT, fg='#008000')
        self._result_label = tk.Label(self, text="", font=(protocol.FONT_NAME, int(1.2 * protocol.FONT_SIZE)),
                                      fg='#27742C')
        self.show_result()
        self.hide_result()
        self._from_combobox = ttk.Combobox(self, values=protocol.CURRENCIES,
                                           font=(protocol.FONT_NAME, int(0.75 * protocol.FONT_SIZE)), state="normal")
        self._to_combobox = ttk.Combobox(self, values=protocol.CURRENCIES,
                                         font=(protocol.FONT_NAME, int(0.75 * protocol.FONT_SIZE)), state="normal")
        self._amount_entry = tk.Entry(self, width=int(protocol.TEXT_WIDTH / 2),
                                      font=(protocol.FONT_NAME, int(0.75 * protocol.FONT_SIZE)))

        self._place_objects()

    def _place_objects(self):
        self._hello_label.place(x=protocol.CENTER_X, y=20) # Average of RIGHT_X AND LEFT_X
        self._switch_button.place(x=340, y=170)
        self._convert_button.place(x=protocol.RIGHT_X, y=115)
        self._history_button.place(x=protocol.RIGHT_X, y=265)
        self._stocks_button.place(x=protocol.RIGHT_X, y=415)
        self._back_button.place(x=protocol.RIGHT_X, y=565)
        self._convert_from_label.place(x=protocol.LEFT_X, y=20)
        self._convert_to_label.place(x=protocol.LEFT_X, y=220)
        self._amount_label.place(x=protocol.LEFT_X, y=420)
        self._from_combobox.place(x=protocol.LEFT_X, y=80)
        self._to_combobox.place(x=protocol.LEFT_X, y=280)
        self._amount_entry.place(x=protocol.LEFT_X, y=480)

    def _on_click_switch(self):
        old_from = self._from_combobox.get()
        protocol.put_text_in_entry(self._from_combobox, self._to_combobox.get())
        protocol.put_text_in_entry(self._to_combobox, old_from)
        log(f"Currencies switched, now {self._from_combobox.get()} to {self._to_combobox.get()}")

    def _on_click_convert(self):
        log("Conversion process started")
        log(f"From {self._from_combobox.get()}")
        log(f"To {self._to_combobox.get()}")
        log(f"Amount: {self._amount_entry.get()}")

        user_info = ("CONVERT", self._from_combobox.get().split()[0], self._to_combobox.get().split()[0],
                     self._amount_entry.get())
        json_info = protocol.make_json(user_info)

        # Send JSON to server
        self.client_bl.send_data(json_info)

    def show_result(self, result: str = ""):
        self._result_label.config(text=result)
        self._result_label.place(x=int(0.85 * protocol.CENTER_X), y=int(0.55 * protocol.CENTER_Y))

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
        self._tree.place(x=protocol.LEFT_X, y=int(0.65 * protocol.CENTER_Y), width=800, height=300)
        self._back_button.place(x=protocol.RIGHT_X, y=int(1.525 * protocol.CENTER_Y))

        # LEFT_X intentionally used here in the y value in order to create a 4:3 rectangle
        self._history_label.place(x=protocol.LEFT_X, y=int(0.75 * protocol.LEFT_X))


class StocksFrame(AppFrame):
    def __init__(self, client_bl):
        # Constructor
        super().__init__(client_bl, "Stocks")

        self._title_label = tk.Label(self, text="Top 6 biggest companies", font=protocol.FONT)
        self._back_button = tk.Button(self, text="Back to currencies", font=protocol.FONT,
                                      command=lambda:self.app_master.show_frame(MainFrame))
        self._my_stocks_button = tk.Button(self, text="My stocks", font=protocol.FONT,
                                           command=lambda:self.app_master.show_frame(BalanceFrame))

        self._company_labels = []
        self._images = []
        self._image_labels = []
        self._buy_buttons = []
        self._sell_buttons = []

        for company in self.app_master.companies:
            # Create text string without exceeding 120-char best practice
            text = f"{company['Name']} ({company['Symbol']})\n{company['Price']}$ ({company['Change']}%)\n"
            text += f"Market cap: {round(company['Market_cap']/1000000, 2)}T$"

            # Color green or red respectively
            if company['Change'] < 0:
                self._company_labels.append(tk.Label(self, text=text, fg="#ef4444",
                                                    font=(protocol.FONT_NAME, int(0.725 * protocol.FONT_SIZE))))
            else:
                self._company_labels.append(tk.Label(self, text=text, fg="#059669",
                                                     font=(protocol.FONT_NAME, int(0.725 * protocol.FONT_SIZE))))

            # Get company logo
            logo_bytes = base64.b64decode(company['Encoded_logo'])
            logo_file = BytesIO(logo_bytes)
            logo_image = protocol.open_image(logo_file, (105, 105))

            # Add objects to lists
            self._images.append(logo_image) # Reference has to be saved
            self._image_labels.append(tk.Label(self, image=logo_image))
            self._buy_buttons.append(tk.Button(self, text="Buy",
                                               font=(protocol.FONT_NAME, int(0.625 * protocol.FONT_SIZE)),
                                               command=lambda n=company['Name']:self._on_click_buy(n)))
            self._sell_buttons.append(tk.Button(self, text="Sell",
                                                font=(protocol.FONT_NAME, int(0.625 * protocol.FONT_SIZE)),
                                                command=lambda n=company['Name']:self._on_click_sell(n)))

        self._place_objects()

    def _place_objects(self):
        # Place general icons
        self._title_label.place(x=int(0.8 * protocol.CENTER_X), y=20)
        self._back_button.place(x=int(0.55 * protocol.CENTER_X), y=580)
        self._my_stocks_button.place(x=int(1.45 * protocol.CENTER_X), y=580)

        # Place first half of companies
        for i in range(int(len(self._company_labels) / 2)):
            self._company_labels[i].place(x=protocol.LEFT_X, y=120 + 150 * i)
            self._image_labels[i].place(x=protocol.LEFT_X + 290, y=120 + 150 * i)
            self._buy_buttons[i].place(x=protocol.LEFT_X + 440, y=120 + 150 * i)
            self._sell_buttons[i].place(x=protocol.LEFT_X + 440, y=190 + 150 * i)

        # Place second half, i = length of first half because in this loop, i starts at the index of
        # the length of the first half
        for i in range(int(len(self._company_labels) / 2), len(self._company_labels)):
            self._company_labels[i].place(x=int(0.95 * protocol.RIGHT_X),
                                          y=120 + 150 * (i - int(len(self._company_labels) / 2)))
            self._image_labels[i].place(x=int(0.95 * protocol.RIGHT_X + 290),
                                        y=120 + 150 * (i - int(len(self._company_labels) / 2)))
            self._buy_buttons[i].place(x=int(0.95 * protocol.RIGHT_X - 120),
                                       y=120 + 150 * (i - int(len(self._company_labels) / 2)))
            self._sell_buttons[i].place(x=int(0.95 * protocol.RIGHT_X - 120),
                                        y=190 + 150 * (i - int(len(self._company_labels) / 2)))

    def _on_click_buy(self, company_name):
        # Update balance
        try:
            found_row = False
            for row in self.app_master.stocks[self.app_master.username]:
                if row[0] == company_name:
                    row[1] += 1
                    found_row = True
                    break
            if not found_row:
                self.app_master.stocks[self.app_master.username].append([company_name, 1])
        except KeyError:
            self.app_master.stocks[self.app_master.username] = [[company_name, 1]]

        # Make JSON
        user_data = ("BUY", company_name)
        json_data = protocol.make_json(user_data)

        # Send JSON to server
        self.client_bl.send_data(json_data)

    def _on_click_sell(self, company_name):
        # Update balance
        try:
            for row in self.app_master.stocks[self.app_master.username]:
                if row[0] == company_name:
                    if row[1] > 1:
                        row[1] -= 1
                        break
                    else:
                        self.app_master.stocks[self.app_master.username].remove(row)
        except KeyError:
            pass

        # Make JSON
        user_data = ("SELL", company_name)
        json_data = protocol.make_json(user_data)

        # Send JSON to server
        self.client_bl.send_data(json_data)


class BalanceFrame(AppFrame):
    def __init__(self, client_bl):
        # Constructor
        super().__init__(client_bl, "My stocks")

        # Create objects
        self._my_stocks_label = tk.Label(self, text="My stocks",
                                         font=(protocol.FONT_NAME, int(1.75 * protocol.FONT_SIZE)))
        self._back_button = tk.Button(self, text="Back", font=protocol.FONT,
                                      command=lambda:self.app_master.show_frame(StocksFrame))

        # Add value to stocks
        stocks_info = []
        price = 0 # Default price
        for entry in self.app_master.stocks[self.app_master.username]:
            for company in self.app_master.companies: # Find the company from entry in the list
                if company['Name'] == entry[0]:
                    price = company['Price']
                    break
            stocks_info.append(entry + [price])

        # Create tree
        try:
            self._tree = protocol.create_table(self.app_master, protocol.STOCKS_TBL_HEADERS, stocks_info)
        except KeyError:
            self._tree = protocol.create_table(self.app_master, protocol.STOCKS_TBL_HEADERS, [])

        # Create portfolio value
        self._portfolio_value: int = 0
        for entry in stocks_info:
            self._portfolio_value += entry[1] * entry[2] # Add amount of stocks * value of each stock
        self._portfolio_value_label = tk.Label(self, text=f"Your portfolio value is {round(self._portfolio_value, 2)}$",
                                               font=protocol.FONT, fg='#008000')

        self._place_objects()

    def _place_objects(self):
        self._tree.place(x=protocol.LEFT_X, y=int(0.65 * protocol.CENTER_Y), width=800, height=300)
        self._back_button.place(x=protocol.RIGHT_X, y=int(1.525 * protocol.CENTER_Y))

        # LEFT_X intentionally used here in the y value in order to create a 4:3 rectangle
        self._my_stocks_label.place(x=protocol.LEFT_X, y=int(0.75 * protocol.LEFT_X))
        self._portfolio_value_label.place(x=protocol.LEFT_X, y=580)


class ErrorFrame(AppFrame):
    def __init__(self, client_bl):
        # Constructor
        super().__init__(client_bl, "Error")

        # Create back button
        self._back_button = tk.Button(self, text="Back to previous page", font=protocol.FONT,
                                      command=lambda:self.app_master.show_frame(type(self.app_master.previous_frame)))

        # Create error text
        x = protocol.RIGHT_X
        y = protocol.CENTER_Y
        self.canvas.create_text(x, y, text="Error: Client is no longer connected to server", fill='#d32f2f',
                                font=protocol.FONT)

        self._place_objects()

    def _place_objects(self):
        self._back_button.place(x=protocol.RIGHT_X, y=580)


class ClientApp(tk.Tk):
    def __init__(self, client_bl):
        # Constructors
        super().__init__()
        self.client_bl = client_bl

        # Create socket if it doesn't already exist
        if not protocol.socket_alive(self.client_bl.socket):
            self.client_bl.on_open()
            Thread(target=self.listen, daemon=True).start()
        log(f"Socket ID: {id(self.client_bl.socket)}")

        # Username is needed for hello
        # Username is effectively public so other classes can use it, made possible with public getter and setter
        # Methods, which are both necessary to log changes to variable value
        self._username = protocol.GUEST_USERNAME

        # Received by the server at signup/login and gradually filled when needed
        self.converts: dict = {}
        self.stocks: dict = {}

        self.companies = None # Will be filled later by the server

        # Used in ErrorFrame to return to previous page
        self.previous_frame = None

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
            # First, send the necessary command for the client
            self.client_bl.send_data(protocol.make_json(["STOCKS"]) + "\n")
            log("Sent stock value request")
            while True:
                # Listen and proceed by instructions from server
                data: str = self.client_bl.socket.recv(protocol.BUFFER_SIZE).decode(protocol.ENCODE_FORMAT)

                # Handle large message logic
                if data.startswith(protocol.LARGE_SYMBOL):
                    # Find length
                    length = int(data.split(protocol.LARGE_SYMBOL)[1])
                    data_bytes = bytearray()
                    while len(data_bytes) < length:
                        # Shouldn't be decoded now in order to calculate bytes length
                        data_bytes.extend(self.client_bl.socket.recv(protocol.BUFFER_SIZE))

                    data = data_bytes.decode(protocol.ENCODE_FORMAT)

                if data.startswith("[") and data.endswith("]") or data.startswith("{") and data.endswith("}"):
                    # Checks if data can be a JSON string
                    response_data = json.loads(data)
                    if response_data[0] == "SIGNUP":
                        log("Signup successful")
                        self.converts[self.username] = response_data[1]
                        self.stocks[self.username] = response_data[2]
                        self.show_frame(MainFrame)
                    elif response_data[0] == "LOGIN":
                        log("Login successful")
                        self.converts[self.username] = response_data[1]
                        self.stocks[self.username] = response_data[2]
                        self.show_frame(MainFrame)
                    elif response_data[0] == "STOCKS":
                        log("Received stock values")
                        self.companies = response_data[1]
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
                elif data == "CLOSE":
                    log("Received close message")
                    self.previous_frame = self._current_frame # Handle previous frame
                    self.show_frame(ErrorFrame)
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
        self._current_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        log(f"{self._current_frame.__class__.__name__} showed")

    def _close_window(self):
        log("Client is shutting down")
        self.client_bl.on_close()
        self.destroy() # Has to be included in order to actually close the window


if __name__ == "__main__":
    # Run client
    bl: ClientBL = ClientBL()
    gui: ClientApp = ClientApp(bl)
    gui.mainloop()

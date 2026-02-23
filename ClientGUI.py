# Imports
from abc import ABC, abstractmethod
from ClientBL import ClientBL
import protocol
from protocol import log
import tkinter as tk
from PIL import Image, ImageTk
from typing import cast
from Frames import MainFrame, StartFrame, ForgotCodeFrame, LoginFrame, HistoryFrame, ForgotSetFrame

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

        # Log socket ID if one exists
        if protocol.socket_alive(self.client_bl.socket):
            log(f"Socket ID: {id(self.client_bl.socket)}")
            # Compare this ID with ID in other frames

        # Canvas
        self._canvas = tk.Canvas(self, width=protocol.SCREEN_WIDTH, height=protocol.SCREEN_HEIGHT)
        self._canvas.pack(fill="both", expand=True)
        self._canvas.create_image(0, 0, image=self._bg_pimage, anchor='nw')

    def create_user_text(self, username: str):
        x = protocol.SCREEN_WIDTH - 180
        y = 50
        self._canvas.create_text(x, y, text=f"👤{username}", fill="#c58917", font=protocol.FONT)

    @abstractmethod
    def _place_objects(self):
        pass # This method must be implemented by every frame individually



class ClientApp(tk.Tk):
    def __init__(self, client_bl):
        # Constructors
        super().__init__()
        self.client_bl = client_bl

        # Username is needed for hello
        # Username is effectively public so other classes can use it, made possible with public getter and setter
        # Methods, which are both necessary to log changes to variable value
        self._username = 'Guest'

        # Convert list is needed for history frame
        self.converts = []

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
                    # This logic only works in current result string, change logic if changing string
                    data_words = data.split()

                    # Log and ignore errors related to conversion error
                    try:
                        source = data_words[1]
                        dest = data_words[4]
                        amount = data_words[0]
                        result = data_words[3]
                        if len(self.converts) == 13: # Maximum capacity
                            self.converts.pop(0)
                        self.converts.append((source, dest, amount, result))
                        log(f"Result message received, source={source}, dest={dest}, amount={amount}, result={result}")
                    except IndexError:
                        log(str(IndexError))
                    self._current_frame.show_result(data)

        except OSError:
            # Exists to log end of listen and ignore errors that show up when the client socket closes
            log("Stopped listening")
            pass

    def show_frame(self, frame):
        if self._current_frame is not None:
            self._current_frame.destroy()
        self._current_frame = frame(self.client_bl) # frame() calls the constructor of any frame (frame class)
        self._current_frame.create_user_text(self.username)
        if isinstance(self._current_frame, HistoryFrame):
            self._current_frame.create_table(self.converts)
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

import protocol
from protocol import log
import tkinter as tk
from ServerBL import ServerBL
from tkinter import PhotoImage

class ServerGUI:
    def __init__(self, server_bl):
        # Get BL
        self._server_bl = server_bl

        # Create root
        self._root = tk.Tk()
        self._root.title(f"{protocol.APP_NAME} - Server")
        self._root.geometry(f"{protocol.SCREEN_WIDTH}x{protocol.SCREEN_HEIGHT}")

        # Show background image
        self._bg_pimage: PhotoImage = protocol.open_image(protocol.BG_PATH, protocol.SCREEN_AREA)
        self._bg_label = tk.Label(self._root, image=self._bg_pimage)
        self._bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create label
        self._server_label = tk.Label(self._root, text="Server", font=(protocol.FONT_NAME, 2 * protocol.FONT_SIZE),
                                      bg='yellow')

        # Create buttons
        self._start_button = tk.Button(self._root, text="Start", font=protocol.FONT, command=self._on_click_start_gui)
        self._stop_button = tk.Button(self._root, text="Stop", font=protocol.FONT, command=self._on_click_stop_gui)
        protocol.reverse_button(self._stop_button)
        self._refresh_button = tk.Button(self._root, text="Refresh", font=protocol.FONT,
                                         command=self._on_click_refresh_gui)

        # Create tree
        self._tree = protocol.create_table(self._root, protocol.SERVER_TBL_HEADERS, self._server_bl.client_list)

        self._place_objects()

    def _place_objects(self):
        self._tree.place(x=protocol.LEFT_X, y=200, width=800, height=300)
        self._server_label.place(x=protocol.LEFT_X, y=35)
        self._start_button.place(x=protocol.RIGHT_X, y=80)
        self._stop_button.place(x=protocol.RIGHT_X, y=230)
        self._refresh_button.place(x=protocol.LEFT_X, y=575)

    def _on_click_start_gui(self):
        protocol.reverse_many_buttons((self._start_button, self._stop_button))
        self._server_bl.on_click_start()

    def _on_click_stop_gui(self):
        protocol.reverse_many_buttons((self._start_button, self._stop_button))
        self._server_bl.on_click_stop()

    def _on_click_refresh_gui(self):
        self._tree.destroy()
        self._tree = protocol.create_table(self._root, protocol.SERVER_TBL_HEADERS, self._server_bl.client_list)
        self._tree.place(x=protocol.LEFT_X, y=200, width=800, height=300)
        log("Table refreshed")

    def run(self):
        self._root.mainloop()


if __name__ == "__main__":
    # Run server
    server_bl = ServerBL()
    server_screen: ServerGUI = ServerGUI(server_bl)
    server_screen.run()
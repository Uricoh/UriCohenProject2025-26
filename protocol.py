import datetime

PORT: int = 8822
SERVER_IP: str = "127.0.0.1"

size1: int = 1500
size2: int = 750
font: tuple = ('Arial', 32)
text_width: int = 20
labels_x: int = 50
buttons_x: int = 1000
bg_path: str = "background.jpg"


def gettimeastext() -> str:
    current_datetime = datetime.datetime.now()
    formatted_datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_datetime_string

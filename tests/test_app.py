import pytest
import tkinter as tk
from serial_monitor.ui.main_window import MainWindow
from serial_monitor.formatters import format_data
import pytest
import os

pytestmark = pytest.mark.skipif(
    os.environ.get("DISPLAY", "") == "" and os.name != "nt",
    reason="No display available for Tkinter"
)
tk.Tk(useTk=False)

@pytest.fixture
def app():
    root = MainWindow()
    yield root
    root.destroy()

def test_format_data_utf8():
    assert format_data("ABC","ABC") == "ABC"

def test_format_data_hex():
    assert format_data("HEX","A") == "41"

def test_format_data_dec():
    assert format_data("DEC","A") == "65"

def test_format_data_bin():
    assert format_data("BIN","A") == "01000001"

def test_send_without_connection(app):
    # Проверим что flash запускается
    app.serial_handler = None
    app.connected = False
    app._send()  # не должно падать

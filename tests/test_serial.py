import pytest
from serial_monitor.serial_io import SerialHandler

class DummySerial:
    def __init__(self, *a, **kw):
        self.is_open = True
        self.in_waiting = 0
        self.buffer = []
        self.dtr = True
        self.rts = True

    def write(self, data):
        self.buffer.append(data)

    def readline(self):
        return b"Hello\n"

    def close(self):
        self.is_open = False

def test_send_and_receive(monkeypatch):
    monkeypatch.setattr("serial_monitor.serial_io.serial.Serial", DummySerial)
    handler = SerialHandler("COM1", 9600)
    handler.ser.in_waiting = 1  # чтобы _read_loop прочитал

    # запускаем один проход
    handler._read_loop_iteration()

    assert handler.queue.get_nowait() == "Hello"

    handler.send("Ping")
    assert handler.ser.buffer[-1] == b"Ping\n"

def test_dtr_rts(monkeypatch):
    monkeypatch.setattr("serial_monitor.serial_io.serial.Serial", DummySerial)
    handler = SerialHandler("COM1", 9600)

    handler.set_dtr(False)
    assert handler.ser.dtr is False

    handler.set_rts(False)
    assert handler.ser.rts is False

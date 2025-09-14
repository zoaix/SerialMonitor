import threading
import time
from serial_monitor.serial_io import SerialHandler

class SerialController:
    def __init__(self):
        self.handler: SerialHandler | None = None
        self.connected = False

    def connect(self, port: str, baudrate: int):
        self.handler = SerialHandler(port, baudrate)
        self.handler.start()
        self.connected = True

    def disconnect(self):
        if self.handler:
            self.handler.stop()
            self.handler = None
        self.connected = False

    def send(self, data: str):
        if self.handler and self.connected:
            self.handler.send(data)

    def send_file(self, path: str, output_controller, mode: str, delay: float):
        def worker():
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if not self.connected:
                        break
                    self.send(line.strip())
                    output_controller.display_sent(line.strip(), mode)
                    time.sleep(delay)
        threading.Thread(target=worker, daemon=True).start()

    def read_lines(self) -> list[str]:
        lines = []
        if self.handler:
            while not self.handler.queue.empty():
                lines.append(self.handler.queue.get())
        return lines

    def set_dtr(self, value: bool):
        if self.handler:
            self.handler.set_dtr(value)

    def set_rts(self, value: bool):
        if self.handler:
            self.handler.set_rts(value)

    @staticmethod
    def available_ports():
        return SerialHandler.available_ports()

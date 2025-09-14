import serial
import serial.tools.list_ports
from threading import Thread, Event
from queue import Queue


class SerialHandler:
    def __init__(self, port: str, baudrate: int, bytesize: int = 8, parity: str = "N",timeout=50):
        
        if timeout:
           timeout = timeout / 1000 #Because we give timout in ms 
        self.ser = serial.Serial(
            port=port, 
            baudrate=baudrate, 
            bytesize=bytesize,
            parity=parity, 
            timeout=timeout
            )
        self.queue: Queue[str] = Queue()
        self.stop_event = Event()
        self.thread = Thread(target=self._read_loop, daemon=True)

    @staticmethod
    def available_ports() -> list[str]:
        return [p.device for p in serial.tools.list_ports.comports()]

    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.ser.is_open:
            self.ser.close()

    def send(self, data: str):
        self.ser.write(data.encode("utf-8") + b"\n")
        
    def set_dtr(self, state: bool):
        if self.ser and self.ser.is_open:
            self.ser.dtr = state

    def set_rts(self, state: bool):
        if self.ser and self.ser.is_open:
            self.ser.rts = state

    def _read_loop(self):
        while not self.stop_event.is_set():
            if self.ser.in_waiting > 0:
                line = self.ser.readline().decode(errors="ignore").strip()
                if line:
                    self.queue.put(line)
                    
    def _read_loop_iteration(self):
        # For testing
        if self.ser.in_waiting > 0:
            line = self.ser.readline().decode(errors="ignore").strip()
            if line:
                self.queue.put(line)

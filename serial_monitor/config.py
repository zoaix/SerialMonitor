import json
from pathlib import Path
from dataclasses import dataclass, asdict

CONFIG_FILE = Path.home() / ".serial_monitor.json"

PARITY_OPTIONS = {
    "None": "N",
    "Even": "E",
    "Odd": "O",
    "Mark": "M",
    "Space": "S",
}

@dataclass
class SerialConfig:
    port: str = ""
    baudrate: int = 9600
    bytesize: int = 8
    parity: str = "N"
    display_mode: str = "UTF-8"
    dtr_default: bool = True
    rts_default: bool = True
    log_path: str = ""
    send_delay_ms: int = 50
    parser_path: str = "" 

ENCODINGS = {
        "UTF-8": lambda x: x,
        "ANSI": lambda x: x.encode("utf-8", errors="ignore").decode("latin1", errors="ignore"),
        "HEX": lambda x: " ".join(f"{ord(c):02X}" for c in x),
        "DEC": lambda x: " ".join(str(ord(c)) for c in x),
        "BIN": lambda x: " ".join(f"{ord(c):08b}" for c in x),
    }

def load_config() -> SerialConfig:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return SerialConfig(**data)
    return SerialConfig()

def save_config(cfg: SerialConfig) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(asdict(cfg), f, indent=2, ensure_ascii=False)

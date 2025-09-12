import json
from pathlib import Path
from dataclasses import dataclass, asdict

CONFIG_FILE = Path.home() / ".serial_monitor.json"

@dataclass
@dataclass
class SerialConfig:
    port: str = ""
    baudrate: int = 9600
    bytesize: int = 8
    display_mode: str = "UTF-8"


def load_config() -> SerialConfig:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return SerialConfig(**data)
    return SerialConfig()

def save_config(cfg: SerialConfig) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(asdict(cfg), f, indent=2, ensure_ascii=False)

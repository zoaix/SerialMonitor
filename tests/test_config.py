import json
from serial_monitor.config import SerialConfig, save_config, load_config, CONFIG_FILE

def test_save_and_load_config(tmp_path, monkeypatch):
    monkeypatch.setattr("serial_monitor.config.CONFIG_FILE", tmp_path / "cfg.json")

    cfg = SerialConfig(port="COM3", baudrate=115200, bytesize=8)
    save_config(cfg)
    loaded = load_config()

    assert loaded.port == "COM3"
    assert loaded.baudrate == 115200
    assert loaded.bytesize == 8

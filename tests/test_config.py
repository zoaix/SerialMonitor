import json
from serial_monitor.config import SerialConfig, save_config, load_config

def test_save_and_load_config(tmp_path, monkeypatch):
    cfg_file = tmp_path / "cfg.json"
    monkeypatch.setattr("serial_monitor.config.CONFIG_FILE", cfg_file)

    cfg = SerialConfig(port="COM5", baudrate=115200, display_mode="HEX", dtr_default=False, rts_default=True)
    save_config(cfg)

    loaded = load_config()
    assert loaded.port == "COM5"
    assert loaded.baudrate == 115200
    assert loaded.display_mode == "HEX"
    assert loaded.dtr_default is False
    assert loaded.rts_default is True

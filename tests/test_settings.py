import pytest
import tkinter as tk
from serial_monitor.ui.settings_window import SettingsWindow
from serial_monitor.config import SerialConfig, save_config, load_config

@pytest.fixture
def app():
    root = tk.Tk()
    yield root
    root.destroy()

def test_save_settings(tmp_path, monkeypatch, app):
    cfg_file = tmp_path / "cfg.json"
    monkeypatch.setattr("serial_monitor.config.CONFIG_FILE", cfg_file)

    win = SettingsWindow(app)
    win.display_mode.set("HEX")
    win.dtr_default.set(False)
    win.rts_default.set(True)
    win.log_path.set(str(tmp_path / "out.log"))

    win._save()

    cfg = load_config()
    assert cfg.display_mode == "HEX"
    assert cfg.dtr_default is False
    assert cfg.rts_default is True
    assert str(cfg.log_path).endswith("out.log")

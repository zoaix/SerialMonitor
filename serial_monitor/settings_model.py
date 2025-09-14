from serial_monitor.config import load_config, save_config, SerialConfig

class SettingsModel:
    def __init__(self):
        self._config: SerialConfig = load_config()

    @property
    def display_mode(self):
        return self._config.display_mode

    @display_mode.setter
    def display_mode(self, value):
        self._config.display_mode = value

    @property
    def dtr_default(self):
        return getattr(self._config, "dtr_default", True)

    @dtr_default.setter
    def dtr_default(self, value):
        self._config.dtr_default = value

    @property
    def rts_default(self):
        return getattr(self._config, "rts_default", True)

    @rts_default.setter
    def rts_default(self, value):
        self._config.rts_default = value

    @property
    def log_path(self):
        return getattr(self._config, "log_path", "")

    @log_path.setter
    def log_path(self, value):
        self._config.log_path = value

    @property
    def send_delay_ms(self):
        return getattr(self._config, "send_delay_ms", 50)

    @send_delay_ms.setter
    def send_delay_ms(self, value):
        self._config.send_delay_ms = value

    @property
    def parser_path(self):
        return getattr(self._config, "parser_path", "")

    @parser_path.setter
    def parser_path(self, value):
        self._config.parser_path = value

    @property
    def config(self) -> SerialConfig:
        return self._config

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)

    def save(self):
        save_config(self._config)

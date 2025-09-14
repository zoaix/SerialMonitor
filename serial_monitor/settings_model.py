from serial_monitor.config import load_config, save_config, SerialConfig, PARITY_OPTIONS


class SettingsModel:
    def __init__(self):
        self._config: SerialConfig = load_config()

    @property
    def bytesize(self):
        return self._config.bytesize

    @bytesize.setter
    def bytesize(self, value):
        self._config.bytesize = value


    @property
    def baudrate(self):
        return self._config.baudrate

    @baudrate.setter
    def baudrate(self, value):
        self._config.baudrate = value


    @property
    def port(self):
        return self._config.port

    @port.setter
    def port(self, value):
        self._config.port = value


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
    def parity(self):
        for name, code in PARITY_OPTIONS.items():
            if self._config.parity == code:
                return code
        return self._config.parity  # fallback

    @parity.setter
    def parity(self, value):
        if value in PARITY_OPTIONS:
            self._config.parity = PARITY_OPTIONS[value]
        elif value in PARITY_OPTIONS.values():
            self._config.parity = value
        else:
            raise ValueError(f"Invalid parity: {value}")
        print(f"In config set to {self._config.parity}")


    @property
    def config(self) -> SerialConfig:
        return self._config

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)

    def save(self):
        save_config(self._config)
        
        

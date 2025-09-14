from serial_monitor.parsers import load_parser_config

class ParserController:
    def __init__(self):
        self.parser = None

    def load(self, path: str):
        self.parser = load_parser_config(path)
        return self.parser

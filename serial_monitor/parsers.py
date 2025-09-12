import json
import re
from typing import Dict, Any, Optional


class LineParser:
    """Базовый парсер строк на основе конфигурации."""

    def __init__(self, config: dict):
        """
        config example:
        {
            "type": "regex" | "csv",
            "pattern": "TEMP:(?P<TEMP>[0-9.]+) HUM:(?P<HUM>[0-9.]+)",
            "delimiter": ",",
            "fields": ["TEMP", "HUM"]
        }
        """
        self.config = config
        self.regex: Optional[re.Pattern] = None
        if config.get("type") == "regex":
            self.regex = re.compile(config["pattern"])

    def parse(self, line: str) -> Dict[str, Any]:
        if self.config["type"] == "regex":
            return self._parse_regex(line)
        elif self.config["type"] == "csv":
            return self._parse_csv(line)
        else:
            return {}

    def _parse_regex(self, line: str) -> Dict[str, Any]:
        if not self.regex:
            return {}
        match = self.regex.search(line.strip())
        if not match:
            return {}
        return {k: self._convert(v) for k, v in match.groupdict().items()}

    def _parse_csv(self, line: str) -> Dict[str, Any]:
        parts = line.strip().split(self.config.get("delimiter", ","))
        fields = self.config.get("fields", [])
        if len(parts) != len(fields):
            return {}
        return {field: self._convert(value) for field, value in zip(fields, parts)}

    def _convert(self, value: str) -> Any:
        """Конвертация строк в float или int."""
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            return value


def load_parser_config(path: str) -> LineParser:
    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return LineParser(config)

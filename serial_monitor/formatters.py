ENCODINGS = {
        "UTF-8": lambda x: x,
        "ANSI": lambda x: x.encode("utf-8", errors="ignore").decode("latin1", errors="ignore"),
        "HEX": lambda x: " ".join(f"{ord(c):02X}" for c in x),
        "DEC": lambda x: " ".join(str(ord(c)) for c in x),
        "BIN": lambda x: " ".join(f"{ord(c):08b}" for c in x),
    }

def format_data(mode : str, data: str) -> str:
        encoder = ENCODINGS.get(mode, ENCODINGS["UTF-8"])
        return encoder(data)
from serial_monitor.formatters import format_data

class OutputController:
    def __init__(self, text_widget, plot_widget):
        self.text_widget = text_widget
        self.plot_widget = plot_widget

    def display_received(self, raw: str, mode: str):
        line = format_data(mode, raw)
        self._append(f"[Receive]: {line}")
        if self.plot_widget:
            self.plot_widget.add_data(raw)

    def display_sent(self, raw: str, mode: str):
        line = format_data(mode, raw)
        self._append(f"[Send]: {line}")

    def _append(self, text: str):
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", text + "\n")
        self.text_widget.configure(state="disabled")
        self.text_widget.yview("end")

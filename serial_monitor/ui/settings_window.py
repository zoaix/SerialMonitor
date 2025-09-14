import tkinter as tk
from tkinter import ttk, filedialog
from serial_monitor.formatters import ENCODINGS

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.model = model
        self.title("Settings")
        self.geometry("400x250")
        self.resizable(False, False)

        # tk-переменные инициализируются значениями из модели
        self.display_mode = tk.StringVar(value=model.config.display_mode)
        self.dtr_default = tk.BooleanVar(value=model.config.dtr_default)
        self.rts_default = tk.BooleanVar(value=model.config.rts_default)
        self.log_path = tk.StringVar(value=model.config.log_path)
        self.send_delay_ms = tk.IntVar(value=model.config.send_delay_ms)
        self.parser_path = tk.StringVar(value=model.config.parser_path)

        self._setup_ui()

    def _setup_ui(self):
        frame = ttk.Frame(self, padding=10)
        frame.pack(expand=True, fill="both")

        # Display mode
        ttk.Label(frame, text="Default display mode:").grid(row=0, column=0, sticky="w", pady=5)
        display_cb = ttk.Combobox(frame, values=tuple(ENCODINGS.keys()),
                                  textvariable=self.display_mode, width=10)
        display_cb.grid(row=0, column=1, sticky="w")

        # DTR / RTS defaults
        ttk.Checkbutton(frame, text="DTR enabled by default", variable=self.dtr_default)\
            .grid(row=1, column=0, columnspan=2, sticky="w", pady=5)

        ttk.Checkbutton(frame, text="RTS enabled by default", variable=self.rts_default)\
            .grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

        # Log path
        ttk.Label(frame, text="Log file:").grid(row=3, column=0, sticky="w", pady=5)
        entry = ttk.Entry(frame, textvariable=self.log_path, width=25)
        entry.grid(row=3, column=1, sticky="w")
        ttk.Button(frame, text="Browse", command=self._choose_log_path).grid(row=3, column=2, padx=5)

        # File send delay
        ttk.Label(frame, text="File send delay (ms):").grid(row=4, column=0, sticky="w", pady=5)
        ttk.Entry(frame, textvariable=self.send_delay_ms, width=6).grid(row=4, column=1, sticky="w")

        # Parser config
        ttk.Label(frame, text="Parser config:").grid(row=5, column=0, sticky="w", pady=5)
        parser_entry = ttk.Entry(frame, textvariable=self.parser_path, width=25)
        parser_entry.grid(row=5, column=1, sticky="w")
        ttk.Button(frame, text="Browse", command=self._choose_parser_file).grid(row=5, column=2, padx=5)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(side="bottom", fill="x", pady=10)
        ttk.Button(btn_frame, text="Save", command=self._save).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right")

    def _choose_log_path(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("All files", "*.*")]
        )
        if filename:
            self.log_path.set(filename)

    def _choose_parser_file(self):
        filename = filedialog.askopenfilename(
            title="Select parser config",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.parser_path.set(filename)

    def _save(self):
        self.model.update(
            display_mode=self.display_mode.get(),
            dtr_default=self.dtr_default.get(),
            rts_default=self.rts_default.get(),
            log_path=self.log_path.get(),
            send_delay_ms=self.send_delay_ms.get(),
            parser_path=self.parser_path.get(),
        )
        self.model.save()
        self.destroy()

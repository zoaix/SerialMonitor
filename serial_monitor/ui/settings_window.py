import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from serial_monitor.config import load_config, save_config
from serial_monitor.formatters import ENCODINGS

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("400x250")
        self.resizable(False, False)

        self.parent = parent
        self.config_data = load_config()

        # локальные копии значений
        self.display_mode = tk.StringVar(value=self.config_data.display_mode)
        self.dtr_default = tk.BooleanVar(value=getattr(self.config_data, "dtr_default", True))
        self.rts_default = tk.BooleanVar(value=getattr(self.config_data, "rts_default", True))
        self.log_path = tk.StringVar(value=getattr(self.config_data, "log_path", ""))
        self.send_delay_ms = tk.IntVar(value=getattr(self.config_data, "send_delay_ms", 50))
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
        self.dtr_cb = ttk.Checkbutton(frame, text="DTR enabled by default", variable=self.dtr_default)
        self.dtr_cb.grid(row=1, column=0, columnspan=2, sticky="w", pady=5)

        self.rts_cb = ttk.Checkbutton(frame, text="RTS enabled by default", variable=self.rts_default)
        self.rts_cb.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

        # Log path
        ttk.Label(frame, text="Log file:").grid(row=3, column=0, sticky="w", pady=5)
        entry = ttk.Entry(frame, textvariable=self.log_path, width=25)
        entry.grid(row=3, column=1, sticky="w")
        browse_btn = ttk.Button(frame, text="Browse", command=self._choose_log_path)
        browse_btn.grid(row=3, column=2, padx=5)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(side="bottom", fill="x", pady=10)

        save_btn = ttk.Button(btn_frame, text="Save", command=self._save)
        save_btn.pack(side="right", padx=5)

        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side="right")
        
        # SENDING DELAY
    
        ttk.Label(frame, text="File send delay (ms):").grid(row=4, column=0, sticky="w", pady=5)
        delay_entry = ttk.Entry(frame, textvariable=self.send_delay_ms, width=6)
        delay_entry.grid(row=4, column=1, sticky="w")

    def _choose_log_path(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("All files", "*.*")]
        )
        if filename:
            self.log_path.set(filename)

    def _save(self):
        # обновляем конфиг
        self.config_data.display_mode = self.display_mode.get()
        self.config_data.dtr_default = self.dtr_default.get()
        self.config_data.rts_default = self.rts_default.get()
        self.config_data.log_path = self.log_path.get()
        self.config_data.send_delay_ms = self.send_delay_ms.get()

        save_config(self.config_data)
        self.destroy()

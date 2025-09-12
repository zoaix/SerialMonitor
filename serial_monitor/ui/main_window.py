import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from serial_monitor.serial_io import SerialHandler
from serial_monitor.config import load_config, save_config, SerialConfig, ENCODINGS
from serial_monitor.ui.plot_tab import PlotTab


class MainWindow(tk.Tk):



    def __init__(self):
        super().__init__()
        self.title("Serial Monitor")
        self.geometry("800x600")

        self.config_data = load_config()
        self.serial_handler: SerialHandler | None = None
        self.connected = False
        # текущий режим отображения
        self.display_mode = tk.StringVar(
            value=self.config_data.display_mode if hasattr(self.config_data, "display_mode") else "UTF-8"
        )

        self._setup_ui()
        self.after(200, self._update_output)

    def _setup_ui(self):
        # Верхняя панель выбора
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x")
        
        # Меню настроек

        menubar = tk.Menu(self)
        self.config(menu=menubar)

        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Preferences...", command=self._open_settings)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        # Выбор порта
        ttk.Label(top_frame, text="Port:").pack(side="left")
        self.port_cb = ttk.Combobox(top_frame, values=SerialHandler.available_ports())
        self.port_cb.set(self.config_data.port)
        self.port_cb.pack(side="left")
        self.port_cb.bind("<Button-1>", lambda e: self._refresh_ports())
        
        # Выбор скорости
        ttk.Label(top_frame, text="Baudrate:").pack(side="left")
        self.baud_cb = ttk.Combobox(top_frame, values=[9600, 19200, 38400, 57600, 115200])
        self.baud_cb.set(self.config_data.baudrate)
        self.baud_cb.pack(side="left")

        # Кнопка Connect\Disconnect
        self.connect_btn = tk.Button(top_frame, text="Connect", command=self._toggle_connection)
        self.connect_btn.pack(side="left")

        # Выбор кодировки
        ttk.Label(top_frame, text="Display:").pack(side="left", padx=5)
        self.display_cb = ttk.Combobox(
            top_frame, values=tuple(ENCODINGS.keys()), textvariable=self.display_mode, width=8
        )
        self.display_cb.pack(side="left")

        # Основные вкладки
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        # Вкладка Output
        output_tab = ttk.Frame(self.notebook)
        self.output_box = scrolledtext.ScrolledText(output_tab, state="disabled")
        self.output_box.pack(expand=True, fill="both")
        self.input_entry = tk.Entry(output_tab)
        self.input_entry.pack(side="left", fill="x", expand=True)
        
        # Send 
        self.input_entry.bind("<Return>", lambda event: self._send())
        send_btn = ttk.Button(output_tab, text="Send", command=self._send)
        send_btn.pack(side="left", padx=5)
        self.notebook.add(output_tab, text="Console")


        # DTR / RTS checkboxes
        self.dtr_var = tk.BooleanVar(value=getattr(self.config_data, "dtr_default", True))
        self.rts_var = tk.BooleanVar(value=getattr(self.config_data, "rts_default", True))

        self.dtr_cb = ttk.Checkbutton(
            output_tab, text="DTR", variable=self.dtr_var, command=self._toggle_dtr
        )
        self.dtr_cb.pack(side="left", padx=5)

        self.rts_cb = ttk.Checkbutton(
            output_tab, text="RTS", variable=self.rts_var, command=self._toggle_rts
        )
        self.rts_cb.pack(side="left", padx=5)

        # Вкладка Plot
        self.plot_tab = PlotTab(self.notebook)
        self.notebook.add(self.plot_tab, text="Plot")

    def _toggle_connection(self):
        if self.connected:
            self._disconnect()
        else:
            self._connect()


    def _toggle_dtr(self):
        if self.serial_handler:
            self.serial_handler.set_dtr(self.dtr_var.get())

    def _toggle_rts(self):
        if self.serial_handler:
            self.serial_handler.set_rts(self.rts_var.get())

    def _connect(self):
        port = self.port_cb.get()
        baudrate = int(self.baud_cb.get())
        cfg = SerialConfig(port=port, baudrate=baudrate)
        cfg.display_mode = self.display_mode.get()
        save_config(cfg)

        try:
            self.serial_handler = SerialHandler(port, baudrate)
            self.serial_handler.start()
            self.connected = True
            self.connect_btn.config(text="Disconnect")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _disconnect(self):
        if self.serial_handler:
            self.serial_handler.stop()
            self.serial_handler = None
        self.connected = False
        self.connect_btn.config(text="Connect")


    def _update_output(self):
        if self.serial_handler:
            while not self.serial_handler.queue.empty():
                raw_line = self.serial_handler.queue.get()
                line = self._format_data(raw_line)
                self._append_output(f"[Receive]: {line}")
                self.plot_tab.process_line(raw_line)
        self.after(200, self._update_output)

    def _append_output(self, text: str):
        self.output_box.configure(state="normal")
        self.output_box.insert("end", text + "\n")
        self.output_box.configure(state="disabled")
        self.output_box.yview("end")

    def _send(self):
        if self.serial_handler and self.connected:
            data = self.input_entry.get()
            self.serial_handler.send(data)
            formatted = self._format_data(data)
            self._append_output(f"[Send]: {formatted}")
            self.input_entry.delete(0, "end")
        else:
            self._flash_button(self.connect_btn, "green")

    def _flash_button(self, button: tk.Button, color: str, flashes: int = 3, interval: int = 200):
        if getattr(button, "_flashing", False):
            return  # уже мигает — новые циклы не запускаем

        button._flashing = True
        default_color = button.cget("background")

        def toggle(count=0):
            if count >= flashes * 2:
                button.config(background=default_color)
                button._flashing = False
                return

            if count % 2 == 0:
                button.config(background=color)
            else:
                button.config(background=default_color)

            self.after(interval, lambda: toggle(count + 1))

        toggle()

    def _refresh_ports(self):
        ports = SerialHandler.available_ports()
        current = self.port_cb.get()
        self.port_cb["values"] = ports

        if current in ports:
            self.port_cb.set(current)
        elif ports:

            self.port_cb.set(ports[0])
        else:
            self.port_cb.set("")
    
    def _format_data(self, data: str) -> str:
        mode = self.display_mode.get()
        encoder = ENCODINGS.get(mode, ENCODINGS["UTF-8"])
        return encoder(data)
    
    def _open_settings(self):
        from serial_monitor.ui.settings_window import SettingsWindow
        SettingsWindow(self)
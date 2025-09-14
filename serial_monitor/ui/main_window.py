import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pathlib import Path
from serial_monitor.config import ENCODINGS
from serial_monitor.settings_model import SettingsModel
from serial_monitor.ui.simple_plot import SimplePlot
from serial_monitor.controllers.serial_controller import SerialController
from serial_monitor.controllers.output_controller import OutputController
from serial_monitor.controllers.parser_controller import ParserController


def get_icon(filepath: str):
    root_path = Path(__file__).resolve().parents[2]
    img_path = root_path / filepath
    return tk.PhotoImage(file=str(img_path))


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Serial Monitor")
        self.geometry("800x600")
        self.iconphoto(False, get_icon("serial_monitor/ui/static/favico/rs-232-color-96.png"))

        # --- зависимости ---
        self.settings = SettingsModel()
        self.serial = SerialController()
        self.parser = ParserController()

        # режим отображения
        self.display_mode = tk.StringVar(value=self.settings.config.display_mode)

        # --- UI ---
        self._setup_ui()
        self.output = OutputController(self.output_box, self.plot_tab)

        # циклический опрос
        self.after(200, self._update_output)

    def _setup_ui(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x")

        
        # Settings 
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Preferences...", command=self._open_settings)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        # Port
        ttk.Label(top_frame, text="Port:").pack(side="left")
        self.port_cb = ttk.Combobox(top_frame, values=self.serial.available_ports())
        self.port_cb.set(self.settings.config.port)
        self.port_cb.pack(side="left")
        self.port_cb.bind("<Button-1>", lambda e: self._refresh_ports())
        self.port_cb.bind("<<ComboboxSelected>>", lambda e: self._on_connection_settings_changed()) 
        
        # Baudrate
        ttk.Label(top_frame, text="Baudrate:").pack(side="left")
        self.baud_cb = ttk.Combobox(top_frame, values=[9600, 19200, 38400, 57600, 115200])
        self.baud_cb.set(self.settings.config.baudrate)
        self.baud_cb.pack(side="left")
        self.baud_cb.bind("<<ComboboxSelected>>", lambda e: self._on_connection_settings_changed()) 


        # Connect button with icons
        self.icon_connect = get_icon("serial_monitor/ui/static/connect_buttons/connect-color-32.png")
        self.icon_disconnect = get_icon("serial_monitor/ui/static/connect_buttons/disconnect-color-32.png")

        style = ttk.Style(self)
        style.configure("Icon.TButton", relief="flat", padding=0, borderwidth=0, padx=5)
        style.map("Icon.TButton",
                  relief=[("pressed", "flat"), ("active", "flat")],
                  background=[("pressed", "!disabled", "white"), ("active", "white")])

        self.connect_btn = ttk.Button(
            top_frame,
            image=self.icon_disconnect,
            command=self._toggle_connection,
            style="Icon.TButton"
        )
        self.connect_btn.pack(side="left")

        # Display mode
        ttk.Label(top_frame, text="Display:").pack(side="left", padx=5)
        self.display_cb = ttk.Combobox(
            top_frame, values=tuple(ENCODINGS.keys()),
            textvariable=self.display_mode, width=8
        )
        self.display_cb.pack(side="left")

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        # Output tab
        output_tab = ttk.Frame(self.notebook)
        self.output_box = scrolledtext.ScrolledText(output_tab, state="disabled")
        self.output_box.pack(expand=True, fill="both")

        entry_frame = ttk.Frame(output_tab)
        entry_frame.pack(side="left", fill="x", expand=True)

        self.input_entry = tk.Entry(entry_frame)
        self.input_entry.pack(side="left", fill="x", expand=True)

        file_btn = ttk.Button(entry_frame, text="📂", width=3, command=self._send_file)
        file_btn.pack(side="left", padx=2)

        send_btn = ttk.Button(entry_frame, text="Send", command=self._send)
        send_btn.pack(side="left", padx=5)

        self.input_entry.bind("<Return>", lambda e: self._send())
        self.notebook.add(output_tab, text="Console")

        # DTR / RTS
        self.dtr_var = tk.BooleanVar(value=self.settings.config.dtr_default)
        self.rts_var = tk.BooleanVar(value=self.settings.config.rts_default)

        self.dtr_cb = ttk.Checkbutton(output_tab, text="DTR", variable=self.dtr_var,
                                      command=lambda: self.serial.set_dtr(self.dtr_var.get()))
        self.dtr_cb.pack(side="left", padx=5)

        self.rts_cb = ttk.Checkbutton(output_tab, text="RTS", variable=self.rts_var,
                                      command=lambda: self.serial.set_rts(self.rts_var.get()))
        self.rts_cb.pack(side="left", padx=5)

        # Plot tab
        self.plot_tab = SimplePlot(self.notebook)
        
        self.notebook.add(self.plot_tab, text="Plot")

    
    def _load_parser(self):
        if self.settings.config.parser_path:
            try:
                self.plot_tab.set_parser(self.parser.load(self.settings.parser_path))
            except Exception as e:
                messagebox.showerror("Parser error", f"Failed to load parser: {e}")
                self.plot_tab.set_parser(None)
        else:
            self.plot_tab.set_parser(None)
    
    def _connection(self):
        if not self.serial.connected:
            
            self.serial.connect()
            self.connect_btn.config(image=self.icon_connect)
            self.plot_tab.set_connected(True)
    
    def _disconnection(self):
        self.serial.disconnect()
        self.connect_btn.config(image=self.icon_disconnect)
        self.plot_tab.set_connected(False)

    # --- connection ---
    def _toggle_connection(self):
        if self.serial.connected:
            self._disconnection()
        else:
            try:
                self._connection()
                
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _on_connection_settings_changed(self):
        new_port = self.port_cb.get()
        new_baudrate = int(self.baud_cb.get())
        if (not new_port) and (new_baudrate>0):
            return
        
        if self.serial.connected:
            self._disconnection()
            self.after(200, self._connection)
        else:
            try:
                self.settings.port = new_port
                self.settings.baudrate= new_baudrate
                self.settings.save()
            except ValueError as e:
                messagebox.showerror("Invalid parameter", str(e)) 
    
    # --- update loop ---
    def _update_output(self):
        for raw in self.serial.read_lines():
            self.output.display_received(raw, self.display_mode.get())
        self.after(200, self._update_output)

    # --- send data ---
    def _send(self):
        data = self.input_entry.get()
        if not data:
            return
        if not self.serial.connected:
            self._flash_button(self.connect_btn, "green")
            return
        self.serial.send(data)
        self.output.display_sent(data, self.display_mode.get())
        self.input_entry.delete(0, "end")

    def _send_file(self):
        if not self.serial.connected:
            self._flash_button(self.connect_btn, "green")
            return

        file_path = filedialog.askopenfilename(
            title="Select file to send",
            filetypes=[("All files", "*.*")]
        )
        if not file_path:
            return

        self.serial.send_file(file_path, self.output, self.display_mode.get(),
                              delay=self.settings.config.send_delay_ms/1000.0)

    # --- helpers ---
    def _refresh_ports(self):
        ports = self.serial.available_ports()
        self.port_cb["values"] = ports
        if self.port_cb.get() not in ports and ports:
            self.port_cb.set(ports[0])

    
    def _flash_button(self, button: ttk.Button, color: str, flashes: int = 3, interval: int = 200):
        if getattr(button, "_flashing", False):
            return
        button._flashing = True
        style = ttk.Style(self)
        flash_style = "Flash.TButton"
        normal_style = button.cget("style") or "TButton"
        default_bg = style.lookup(normal_style, "background")

        def toggle(count=0):
            if count >= flashes * 2:
                style.configure(flash_style, background=default_bg)
                button.configure(style=normal_style)
                button._flashing = False
                return
            style.configure(flash_style, background=color if count % 2 == 0 else default_bg)
            button.configure(style=flash_style)
            self.after(interval, lambda: toggle(count + 1))

        toggle()
        
    def _open_settings(self):
        from serial_monitor.ui.settings_window import SettingsWindow

        win = SettingsWindow(self, self.settings)
        self.wait_window(win)  # ждём закрытия окна
        self._load_parser()
        if self.serial.connected:
            self._disconnection()
            self.after(200, self._connection)


# Serial Monitor

A lightweight Python serial port monitor with a Tkinter GUI.
Features include:
- Console view for incoming and outgoing data.
- Send text or files to the serial port.
- Configurable encoding display (UTF-8, ANSI, HEX, DEC, BIN).
- Simple live plotting of parsed sensor values.
- Customizable parsers (Regex or CSV).
- User preferences stored in ~/.serial_monitor.json.

# Installation

## Requirements:

- Python 3.12+
- Tkinter 0.1.0+
- pyserial 3.5+

## Dependencies listed in pyproject.toml:

```bash
python -m venv venv
# for linux
source venv/bin/activate
# for windows
.venv\Scripts\activate

pip install -r requirements.txt
```

or, if using Poetry(recomendated):

```bash
poetry install
```

## Run the app:

```bash
python -m serial_monitor.app
```

Or via Poetry:

```bash
poetry run serial-monitor
```

# Usage
## 1. Main Window
When you start the application, you’ll see two main tabs:
1. Console Tab
2. View incoming data(plot)

- Send messages manually (press Enter or click Send).
- Send files using the 📂 button.
- Toggle DTR and RTS signals.

### Plot Tab

Displays parsed sensor values in real time.

Supports zooming:
1. Mouse wheel → time scale (X axis).
2. Shift + Mouse wheel → Y axis scaling.

## 2. Connection

Select Port and Baudrate from the dropdowns.

Click the 🔌 Connect button.
If not connected, pressing Send flashes the button as a reminder.

## 3. Settings

Open Settings → Preferences… in the menu.

Here you can configure:
- Display Mode: UTF-8, ANSI, HEX, DEC, BIN
- Parity: None, Even, Odd, Mark, Space
- DTR/RTS defaults
- Log file path for saving communication(#TODO)
- Send delay between file lines
- Parser config file (JSON)

❗Settings are automatically saved to ~/.serial_monitor.json.

## 4. Parsers

Parsers allow you to extract structured values for plotting.
Example Regex parser (in exaple/temp_n_num.json):

```json
{
  "type": "regex",
  "pattern": "TEMP:(?P<TEMP>[0-9.]+) HUM:(?P<HUM>[0-9.]+)"
}
```

With sample input (in exaple/temp_n_hum_values.txt):


```bash
TEMP:23.4 HUM:50.1
TEMP:22.8 HUM:48.7
```


⬆️This produces two series: TEMP and HUM, both plotted in the graph.

# Shortcuts

- Enter → send message.
- Mouse wheel → zoom time axis.
- Shift + Mouse wheel → zoom Y axis.

License

MIT — see LICENSE


import tkinter as tk
import time
import numpy as np
import random


class SimplePlot(tk.Frame):
    def __init__(self, parent, time_window=10):
        super().__init__(parent)

        self.data_history = {}   # { "TEMP": [(t, v), ...], ... }
        self.colors = {}
        self.available_colors = ["red", "blue", "green", "orange", "purple", "brown"]
        self.max_points = 1000

        self.last_update = None
        self.frozen = False
        self.margin = 40

        # предопределённые шкалы времени
        self.time_scales = [1, 5, 10, 30, 60, 120, 300, 600]
        self.time_index = self.time_scales.index(time_window) if time_window in self.time_scales else 2
        self.time_window = self.time_scales[self.time_index]
        self.frame_ms_delay = 100
        # ручной масштаб Y (None = авто)
        self.y_max_manual = None

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Configure>", lambda e: self._draw_static_elements())

        # zoom колесиком
        self.canvas.bind("<MouseWheel>", self._on_zoom)   # Windows
        self.canvas.bind("<Button-4>", self._on_zoom)     # Linux scroll up
        self.canvas.bind("<Button-5>", self._on_zoom)     # Linux scroll down

        self._update_frame()

    def _on_zoom(self, event):
        """Масштабирование: без Shift — время, с Shift — Y"""
        if getattr(event, "num", None) == 5 or event.delta < 0:
            direction = -1
        elif getattr(event, "num", None) == 4 or event.delta > 0:
            direction = 1
        else:
            return

        if event.state & 0x0001:  # Shift зажат → управление Y
            if self.y_max_manual is None:
                self.y_max_manual = 100

            if direction > 0:  # вверх
                if self.y_max_manual < 100:
                    self.y_max_manual = 100
                elif self.y_max_manual < 110:
                    self.y_max_manual = 110
                elif self.y_max_manual < 150:
                    self.y_max_manual = 150
                elif self.y_max_manual < 200:
                    self.y_max_manual = 200
                elif self.y_max_manual < 300:
                    self.y_max_manual = 300
                else:
                    self.y_max_manual = int(self.y_max_manual * 1.5)
            else:  # вниз
                if self.y_max_manual > 300:
                    self.y_max_manual //= 2
                elif self.y_max_manual > 200:
                    self.y_max_manual = 200
                elif self.y_max_manual > 150:
                    self.y_max_manual = 150
                elif self.y_max_manual > 110:
                    self.y_max_manual = 110
                else:
                    self.y_max_manual = 100
        else:  # управление временем
            new_index = self.time_index + direction
            if 0 <= new_index < len(self.time_scales):
                self.time_index = new_index
                self.time_window = self.time_scales[self.time_index]

        self._draw_static_elements()

    def add_point(self, key, value):
        ts = time.time()
        if key not in self.data_history:
            self.data_history[key] = []
            self.colors[key] = self._random_color()
        self.data_history[key].append((ts, value))
        self.last_update = ts

        # ограничиваем историю
        cutoff = ts - (max(self.time_scales) * 2)
        self.data_history[key] = [(t, v) for t, v in self.data_history[key] if t >= cutoff]

    def _random_color(self):
        return f"#{random.randint(0, 0xFFFFFF):06x}"

    def _draw_static_elements(self):
        """Рисуем оси и подписи"""
        self.canvas.delete("axes")

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        plot_w = w - 2 * self.margin
        plot_h = h - 2 * self.margin

        x0 = self.margin
        y0 = h - self.margin

        # оси
        self.canvas.create_line(x0, self.margin, x0, y0, fill="black", tags="axes")
        self.canvas.create_line(x0, y0, w - self.margin, y0, fill="black", tags="axes")

        # подписи X
        if self.time_window:
            for i in range(6):
                t = self.time_window * i / 5
                x = x0 + t / self.time_window * plot_w
                self.canvas.create_line(x, y0, x, y0 + 5, fill="black", tags="axes")
                label = f"-{int(self.time_window - t)}s"
                self.canvas.create_text(x, y0 + 15, text=label, anchor="n", tags="axes")

        # подписи Y (по ручному масштабу или дефолтному 100)
        max_v = self.y_max_manual if self.y_max_manual else 100
        for i in range(5):
            val = max_v * i / 4
            y = y0 - (val / max_v) * plot_h
            self.canvas.create_line(x0 - 5, y, x0, y, fill="black", tags="axes")
            self.canvas.create_text(5, y, text=f"{val:.1f}", anchor="w", tags="axes")

    def _update_frame(self):
        self.after(self.frame_ms_delay, self._refresh_plot)
    
    
    def _refresh_plot(self):
        self.canvas.delete("lines")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        plot_w = w - 2 * self.margin
        plot_h = h - 2 * self.margin
        now = time.time()

        if not self.data_history:
            self._update_frame()
            return

        min_t = now - self.time_window if self.time_window and not self.frozen else \
                (self.last_update - self.time_window if self.time_window else 0)

        all_values = [
            v for series in self.data_history.values()
            for t, v in series if not self.time_window or t >= min_t
        ]
        if not all_values:
            self._update_frame()
            return

        min_v, max_v = min(all_values), max(all_values)
        if min_v == max_v:
            min_v -= 1
            max_v += 1
        if self.y_max_manual:
            max_v = self.y_max_manual
            min_v = 0

        x0 = self.margin
        y0 = h - self.margin

        for key, series in self.data_history.items():
            points = [(t, v) for t, v in series if t >= min_t] if self.time_window else series
            if len(points) < 2:
                continue

            xs = [x0 + (t - min_t) / self.time_window * plot_w for t, _ in points]
            ys = [y0 - (v - min_v) / (max_v - min_v) * plot_h for _, v in points]

            coords = list(np.ravel(np.column_stack([xs, ys])))
            self.canvas.create_line(*coords, fill=self.colors[key], width=3, tags="lines")

        self._update_frame()

    # --- интеграция с MainWindow ---
    def set_parser(self, parser):
        self.parser = parser

    def set_connected(self, state: bool):
        self.connected = state
        self.frozen = not state

    def add_data(self, line: str):
        if not self.parser:
            return
        parsed = self.parser.parse(line)
        if not parsed:
            return

        ts = time.time()
        self.last_update = ts
        self.frozen = False
        for key, value in parsed.items():
            if not isinstance(value, (int, float)):
                continue
            if key not in self.data_history:
                self.data_history[key] = []
                color = self.available_colors[len(self.colors) % len(self.available_colors)]
                self.colors[key] = color
            self.data_history[key].append((ts, value))
            if len(self.data_history[key]) > self.max_points:
                self.data_history[key] = self.data_history[key][-self.max_points:]

import tkinter as tk
import time
import numpy as np
import random


class SimplePlot(tk.Frame):
    def __init__(self, parent, time_window=10):
        super().__init__(parent)

        self.time_window = time_window
        self.data_history = {}   # { "TEMP": [(t, v), ...], ... }
        self.colors = {}
        self.available_colors = ["red", "blue", "green", "orange", "purple", "brown"]
        self.max_points = 1000
        
        self.last_update = None
        self.frozen = False
        self.margin = 40

        # --- один Canvas ---
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill="both", expand=True)

        # при изменении размера перерисовываем фон (оси/подписи)
        self.canvas.bind("<Configure>", lambda e: self._draw_static_elements())

        # запуск обновления графика
        self.after(100, self._refresh_plot)

    def add_point(self, key, value):
        ts = time.time()
        if key not in self.data_history:
            self.data_history[key] = []
            self.colors[key] = self._random_color()
        self.data_history[key].append((ts, value))
        self.last_update = ts

        # ограничиваем историю
        cutoff = ts - (self.time_window * 2 if self.time_window else 60)
        self.data_history[key] = [(t, v) for t, v in self.data_history[key] if t >= cutoff]

    def set_time_window(self, seconds):
        self.time_window = seconds
        self._draw_static_elements()

    def _random_color(self):
        return f"#{random.randint(0, 0xFFFFFF):06x}"

    def _draw_static_elements(self):
        """Рисуем оси, сетку и подписи (редко)."""
        self.canvas.delete("axes")

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        plot_w = w - self.margin
        plot_h = h - self.margin

        # оси
        self.canvas.create_line(self.margin, 0, self.margin, plot_h, fill="black", tags="axes")
        self.canvas.create_line(self.margin, plot_h, w, plot_h, fill="black", tags="axes")

        # подписи X (по времени)
        if self.time_window:
            for i in range(6):
                t = self.time_window * i / 5
                x = self.margin + t / self.time_window * plot_w
                self.canvas.create_line(x, plot_h, x, plot_h + 5, fill="black", tags="axes")
                label = f"-{int(self.time_window - t)}s"
                self.canvas.create_text(x, plot_h + 15, text=label, anchor="n", tags="axes")

        # подписи Y (деления 5 штук, равномерно)
        # масштаб берём "условный", чтобы при первом запуске что-то показать
        min_v, max_v = 0, 100
        for i in range(5):
            val = min_v + (max_v - min_v) * i / 4
            y = plot_h - (val - min_v) / (max_v - min_v) * plot_h
            self.canvas.create_line(self.margin - 5, y, self.margin, y, fill="black", tags="axes")
            self.canvas.create_text(5, y, text=f"{val:.1f}", anchor="w", tags="axes")


    def _refresh_plot(self):
        self.canvas.delete("lines")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        plot_w = w - self.margin
        plot_h = h - self.margin
        now = time.time()

        if not self.data_history:
            self.after(100, self._refresh_plot)
            return

        if self.time_window and not self.frozen:
            min_t = now - self.time_window
        else:
            min_t = (self.last_update - self.time_window) if self.time_window else 0

        # собрать значения для масштаба
        all_values = [
            v for series in self.data_history.values()
            for t, v in series if not self.time_window or t >= min_t
        ]
        if not all_values:
            self.after(100, self._refresh_plot)
            return

        min_v, max_v = min(all_values), max(all_values)
        if min_v == max_v:
            min_v -= 1
            max_v += 1

        # --- графики ---
        for key, series in self.data_history.items():
            if self.time_window:
                points = [(t, v) for t, v in series if t >= min_t]
            else:
                points = series
            if len(points) < 2:
                continue

            xs = [self.margin + (t - min_t) / self.time_window * plot_w for t, _ in points] if self.time_window else [
                self.margin + i / len(points) * plot_w for i in range(len(points))
            ]
            ys = [plot_h - (v - min_v) / (max_v - min_v) * plot_h for _, v in points]

            coords = list(np.ravel(np.column_stack([xs, ys])))
            self.canvas.create_line(*coords, fill=self.colors[key], width=2, tags="lines")

        self.after(100, self._refresh_plot)

    # --- интеграция с MainWindow ---
    def set_parser(self, parser):
        self.parser = parser
        
    def set_connected(self, state: bool):
        self.connected = state
        if not state:
            self.frozen = True  # freeze при disconnect
        else:
            self.frozen = False
            
    def add_data(self, line: str):
        if not self.parser:
            return
        parsed = self.parser.parse(line)
        if not parsed:
            return

        ts = time.time()
        self.last_update = ts
        self.frozen = False  # снимаем заморозку, если пришли данные
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

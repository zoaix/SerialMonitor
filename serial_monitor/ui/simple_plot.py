# serial_monitor/ui/simple_plot.py
import tkinter as tk
from tkinter import ttk
import time
import numpy as np


class SimplePlot(ttk.Frame):
    def __init__(self, parent, parser=None):
        super().__init__(parent)

        self.parser = parser
        self.data_history = {}   # {"TEMP": [(t, v), ...]}
        self.max_points = 1000
        self.connected = False

        # --- canvas ---
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(expand=True, fill="both")

        self.colors = {}
        self.available_colors = ["red", "blue", "green", "orange", "purple", "brown"]

        self.after(100, self._refresh_plot)

    def set_parser(self, parser):
        self.parser = parser

    def set_connected(self, state: bool):
        """Обновить состояние подключения"""
        self.connected = state
        if not state:
            # просто перестаем обновлять, но данные не трогаем
            pass

    def add_data(self, line: str):
        """Добавляем строку из MainWindow"""
        if not self.parser:
            return
        parsed = self.parser.parse(line)
        if not parsed:
            return

        ts = time.time()
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

    def _refresh_plot(self):
        self.canvas.delete("all")

        if not self.data_history:
            self.after(100, self._refresh_plot)
            return

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        now = time.time()
        time_window = 10  # секунд
        min_t = now - time_window

        # соберем все значения для масштаба
        all_values = [v for series in self.data_history.values() for _, v in series if _ >= min_t]
        if not all_values:
            self.after(100, self._refresh_plot)
            return

        min_v, max_v = min(all_values), max(all_values)
        if min_v == max_v:
            min_v -= 1
            max_v += 1

        for key, series in self.data_history.items():
            points = [(t, v) for t, v in series if t >= min_t]
            if len(points) < 2:
                continue

            xs = [(t - min_t) / time_window * w for t, _ in points]
            ys = [h - (v - min_v) / (max_v - min_v) * h for _, v in points]

            coords = list(np.ravel(np.column_stack([xs, ys])))
            self.canvas.create_line(*coords, fill=self.colors[key], width=2)

        self.after(100, self._refresh_plot)

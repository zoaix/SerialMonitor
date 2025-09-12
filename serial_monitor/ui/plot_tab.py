import tkinter as tk
from tkinter import ttk, filedialog
import matplotlib

matplotlib.use("TkAgg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class PlotTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Live Data")

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(expand=True, fill="both")

        self.data = []

    def process_line(self, line: str):
        try:
            value = float(line)
            self.data.append(value)
            if len(self.data) > 100:
                self.data.pop(0)
            self.ax.clear()
            self.ax.plot(self.data, label="Value")
            self.ax.legend()
            self.canvas.draw()
        except ValueError:
            pass

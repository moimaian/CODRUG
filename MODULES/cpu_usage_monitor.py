# SPDX-License-Identifier: GPL-3.0-or-later
#
# CODRUG – Computational Drug Discovery Platform
# Copyright (C) 2024–2026 Moisés Maia
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

import sys
import time
from collections import deque

try:
    import psutil
except Exception:  # fallback leve
    psutil = None

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtWidgets import QSizePolicy

# Matplotlib backend for Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class CpuWorker(QThread):
    cpu_read = pyqtSignal(float)

    def __init__(self, interval_sec=0.5, parent=None):
        super().__init__(parent)
        self._interval = interval_sec
        self._running = True

    def run(self):
        # Primeira leitura do psutil retorna média desde o boot; segunda em diante é a “instantânea”
        if psutil is not None:
            _ = psutil.cpu_percent(interval=None)
        while self._running:
            if psutil is not None:
                val = psutil.cpu_percent(interval=None)
            else:
                # Fallback tosco: sem psutil estimamos ~0% (evita quebrar caso psutil não esteja instalado)
                val = 0.0
            self.cpu_read.emit(float(val))
            time.sleep(self._interval)

    def stop(self):
        self._running = False


class _CpuFigure(FigureCanvas):
    """Canvas do Matplotlib para plotar CPU % em tempo real."""
    def __init__(self, max_seconds=60, sample_every=0.5, parent=None):
        fig = Figure(figsize=(6, 2.2), tight_layout=True)
        super().__init__(fig)
        self.setParent(parent)
        self.ax = fig.add_subplot(111)
        self.ax.set_title("Uso de CPU (%)", fontsize=11, fontweight="bold")
        self.ax.set_xlabel("Tempo (s)")
        self.ax.set_ylabel("%")
        self.ax.set_ylim(0, 100)
        self.ax.grid(True, alpha=0.25)

        self.max_points = int(max_seconds / sample_every)
        self.dt = sample_every
        self.x = deque(maxlen=self.max_points)
        self.y = deque(maxlen=self.max_points)
        self._t0 = time.time()

        # Linha
        (self.line,) = self.ax.plot([], [], lw=2)

        # Ajuste de crescimento horizontal
        self.ax.set_xlim(0, max_seconds)

    def append_point(self, cpu_pct: float):
        t = time.time() - self._t0
        self.x.append(t)
        self.y.append(cpu_pct)

        if len(self.x) > 2:
            # Ajuste eixos x conforme o tempo (janela deslizante)
            xmax = max(self.x[-1], self.ax.get_xlim()[1])
            xmin = max(0, xmax - (self.max_points * self.dt))
            self.ax.set_xlim(xmin, xmax)

        self.line.set_data(self.x, self.y)
        self.draw_idle()


class CpuUsageWindow(QDialog):
    """Janela que exibe o gráfico de CPU em tempo real."""
    def __init__(self, parent=None, title="Uso de CPU (tempo real)", update_every=0.5):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(False)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        layout = QVBoxLayout(self)

        self.lbl = QLabel("Monitorando uso de CPU…", self)
        self.lbl.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.lbl)

        self.canvas = _CpuFigure(max_seconds=60, sample_every=update_every, parent=self)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.canvas)

        self.worker = CpuWorker(interval_sec=update_every, parent=self)
        self.worker.cpu_read.connect(self._on_cpu_value)

        # Atualiza label suavemente (opcional)
        self._label_timer = QTimer(self)
        self._label_timer.setInterval(1000)
        self._label_timer.timeout.connect(self._refresh_label)
        self._last_value = 0.0

        self.resize(640, 280)

    def start(self):
        self.show()
        self.worker.start()
        self._label_timer.start()

    def _on_cpu_value(self, value: float):
        self._last_value = value
        self.canvas.append_point(value)

    def _refresh_label(self):
        self.lbl.setText(f"Monitorando uso de CPU…  {self._last_value:.1f}%")

    def stop_and_close(self):
        try:
            if self.worker.isRunning():
                self.worker.stop()
                self.worker.wait(1500)
        finally:
            self._label_timer.stop()
            self.close()


class CpuUsageGuard:
    """
    Context manager para uso simples:
        with CpuUsageGuard(self, "Meu Título"):
            # sua tarefa longa
            ...
    A janela abre ao entrar e fecha ao sair (mesmo em exceção).
    """
    def __init__(self, parent=None, title="Uso de CPU (tempo real)", update_every=0.5):
        self.window = CpuUsageWindow(parent=parent, title=title, update_every=update_every)

    def __enter__(self):
        self.window.start()
        return self.window

    def __exit__(self, exc_type, exc, tb):
        self.window.stop_and_close()
        # Não suprime exceções
        return False

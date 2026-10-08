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

"""Janela independente de monitoramento de CPU/GPU.

Roda como um PROCESSO separado (não uma QThread) do CODRUG.py principal, de propósito: o monitor de
CPU/GPU embutido no canto superior direito da janela principal usa um QTimer que só dispara quando o
event loop do Qt da janela principal está livre. Como a STEP 6 (Screening/Tuning/Cross-Validation/Plot)
roda de forma síncrona na própria thread da GUI (para evitar os crashes nativos causados por QThreads em
background nesses cálculos), o event loop da janela principal fica bloqueado durante esses cálculos — e
com ele, qualquer widget da MESMA aplicação/processo, mesmo que os dados venham de uma QThread separada,
já que a repintura da tela também depende do event loop do Qt (que não roda enquanto a thread principal
está presa dentro de uma chamada Python/C síncrona).

Por isso essa janela é um script standalone com seu próprio QApplication, event loop e interpretador
Python — um processo do sistema operacional totalmente independente do processo do CODRUG.py — o que
garante que ela continue atualizando a cada 1,5s mesmo com a janela principal completamente travada.
"""

import shutil
import subprocess
import sys

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QDialog, QHBoxLayout, QLabel, QVBoxLayout

try:
    import psutil
except Exception:
    psutil = None


def _mon_ss(color):
    return (
        f"QLabel{{padding:6px 10px;border:2px solid {color};"
        f"border-radius:6px;background:#0D1B2A;color:{color};"
        f"font-weight:bold;font-size:11pt;}}"
    )


def _uc(percent):
    return "#F57C6F" if percent > 80 else "#E67E22" if percent > 50 else "#27AE60"


def _tc(temp_celsius):
    return "#F57C6F" if temp_celsius > 80 else "#E67E22" if temp_celsius > 60 else "#27AE60"


class HwMonitorWindow(QDialog):
    """Réplica standalone do monitor de CPU/GPU exibido no canto da janela principal do CODRUG."""

    def __init__(self):
        super().__init__(None)
        self.setWindowTitle("CODRUG - CPU/GPU Monitor")
        self.setStyleSheet("background-color:#12202E;")
        self.resize(420, 160)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        title = QLabel("Real-time hardware usage")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color:#C9D1D9; font-weight:bold; font-size:11pt;")
        layout.addWidget(title)

        row = QHBoxLayout()
        row.setSpacing(10)
        self.lbl_cpu = QLabel("CPU: --")
        self.lbl_cpu.setAlignment(Qt.AlignCenter)
        self.lbl_cpu.setStyleSheet(_mon_ss("#27AE60"))
        row.addWidget(self.lbl_cpu, 1)

        self._has_nvidia = shutil.which("nvidia-smi") is not None
        self.lbl_gpu = QLabel("GPU: --")
        self.lbl_gpu.setAlignment(Qt.AlignCenter)
        self.lbl_gpu.setStyleSheet(_mon_ss("#2980B9"))
        self.lbl_gpu.setVisible(self._has_nvidia)
        row.addWidget(self.lbl_gpu, 1)
        layout.addLayout(row)

        note = QLabel(
            "This window runs in its own process, so it keeps updating even while\n"
            "CODRUG's main window is busy (e.g. running STEP 6 Screening/Tuning)."
        )
        note.setAlignment(Qt.AlignCenter)
        note.setWordWrap(True)
        note.setStyleSheet("color:#6E8CA8; font-size:8pt;")
        layout.addWidget(note)

        self._timer = QTimer(self)
        self._timer.setInterval(1500)
        self._timer.timeout.connect(self._update_hw)
        self._timer.start()
        self._update_hw()

    def _update_hw(self):
        if psutil is None:
            self.lbl_cpu.setText("CPU monitor unavailable")
            self.lbl_cpu.setTextFormat(Qt.PlainText)
            self.lbl_cpu.setStyleSheet(_mon_ss("#E67E22"))
        else:
            try:
                per_core = psutil.cpu_percent(interval=None, percpu=True)
                if per_core:
                    cpu_avg = sum(per_core) / len(per_core)
                    cpu_max = max(per_core)
                else:
                    cpu_avg = 0.0
                    cpu_max = 0.0

                temp_suffix = ""
                try:
                    for key in ("coretemp", "k10temp", "acpitz", "cpu_thermal"):
                        readings = psutil.sensors_temperatures().get(key)
                        if readings:
                            temp_color = _tc(readings[0].current)
                            temp_suffix = f"<br><span style='color:{temp_color};'>{readings[0].current:.0f}°C</span>"
                            break
                except Exception:
                    pass

                cpu_color = _uc(cpu_max)
                mem = psutil.virtual_memory()
                mem_used_gb = (mem.total - mem.available) / 1073741824
                mem_total_gb = mem.total / 1073741824
                mem_suffix = f"<br><span style='color:#2980B9;'>{mem_used_gb:.1f}/{mem_total_gb:.1f} GB</span>"
                self.lbl_cpu.setText(
                    f"<span style='color:{cpu_color};'>CPU avg {cpu_avg:.0f}%</span><br>"
                    f"<span style='color:{cpu_color};'>max {cpu_max:.0f}%</span>{temp_suffix}{mem_suffix}"
                )
                self.lbl_cpu.setTextFormat(Qt.RichText)
                self.lbl_cpu.setStyleSheet(_mon_ss(cpu_color))
            except Exception:
                self.lbl_cpu.setText("CPU: --")
                self.lbl_cpu.setTextFormat(Qt.PlainText)
                self.lbl_cpu.setStyleSheet(_mon_ss("#27AE60"))

        if not self._has_nvidia:
            return

        try:
            raw = subprocess.check_output(
                [
                    "nvidia-smi",
                    "--query-gpu=utilization.gpu,temperature.gpu,memory.used,memory.total",
                    "--format=csv,noheader,nounits",
                ],
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=2,
            ).strip()
            first_line = raw.splitlines()[0]
            gpu_util, gpu_temp, mem_used, mem_total = [part.strip() for part in first_line.split(",")[:4]]
            gpu_util_value = float(gpu_util)
            gpu_temp_value = float(gpu_temp)
            gpu_color = _uc(gpu_util_value)
            temp_color = _tc(gpu_temp_value)
            self.lbl_gpu.setText(
                f"<span style='color:{gpu_color};'>GPU {gpu_util_value:.0f}%</span><br>"
                f"<span style='color:{temp_color};'>{gpu_temp_value:.0f}°C</span><br>"
                f"<span style='color:#2980B9;'>{mem_used}/{mem_total} MB</span>"
            )
            self.lbl_gpu.setTextFormat(Qt.RichText)
            self.lbl_gpu.setStyleSheet(_mon_ss(gpu_color))
        except Exception:
            self.lbl_gpu.setText("GPU: --")
            self.lbl_gpu.setTextFormat(Qt.PlainText)
            self.lbl_gpu.setStyleSheet(_mon_ss("#2980B9"))


def main():
    app = QApplication(sys.argv)
    window = HwMonitorWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

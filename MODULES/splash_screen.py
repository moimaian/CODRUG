# splash_screen.py — ícone + barra (0→100 real, início imediato)
# -*- coding: utf-8 -*-

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


import os
import sys
import subprocess
from pathlib import Path
from threading import Thread

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap, QGuiApplication
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar

# -------- Paths & constants --------
HOME = str(Path.home())
APP_DIR = os.path.join(HOME, "CODRUG")
VENV_DIR = os.path.join(HOME, ".venv", "CODRUG")
VENV_PY  = os.path.join(VENV_DIR, "bin", "python")
DESKTOP_DIR  = os.path.join(HOME, ".local", "share", "applications")
DESKTOP_FILE = os.path.join(DESKTOP_DIR, "CODRUG.desktop")
MIN_MARKER   = os.path.join(VENV_DIR, ".codrug_minimal_done")

# Pacotes essenciais (apenas os necessários ao ARQUIVO PRINCIPAL)
ESSENTIALS = [
    "matplotlib>=3.8,<3.9",
    "numpy>=1.26,<2.0",
    "pandas>=2.1,<2.2",
    "psutil>=5.9,<6.0",
    "scipy>=1.11,<1.12",
    "seaborn>=0.13,<0.14",              
    "chembl-webresource-client>=0.10.8,<0.11",
]

# -------- Helpers --------
def _run(cmd):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

def _write_desktop():
    os.makedirs(DESKTOP_DIR, exist_ok=True)
    icon_path = os.path.join(APP_DIR, "ICONS", "CODRUG.png")
    content = f"""[Desktop Entry]
Version=2025.2
Name=CODRUG
Comment= QSAR analysis and machine learning tool
Exec=bash -i -c "env PYTHONNOUSERSITE=1 '{VENV_PY}' '{os.path.join(APP_DIR,'CODRUG.py')}'"
Icon={icon_path}
Terminal=true
Type=Application
Categories=Qt;Science;Chemistry;Education;
StartupNotify=false
"""
    with open(DESKTOP_FILE, "w") as f:
        f.write(content)
    os.chmod(DESKTOP_FILE, 0o755)

def ensure_desktop():
    try:
        if not os.path.isfile(DESKTOP_FILE):
            _write_desktop()
        else:
            with open(DESKTOP_FILE, "r") as f:
                if VENV_PY not in f.read():
                    _write_desktop()
    except Exception:
        pass

def _safe_version(pkg: str) -> str:
    try:
        from importlib import metadata as md
        return md.version(pkg)
    except Exception:
        return None

def need_install_essentials():
    missing = []
    for spec in ESSENTIALS:
        name = spec.split("==")[0].split(">=")[0].split("<")[0].strip()
        if not _safe_version(name):
            missing.append(spec)
    return missing

def install_minimal_essentials(callback=None):
    """
    Instala o mínimo essencial APÓS a splash abrir, só na 1ª vez.
    Escreve um marker em ~/.venv/CODRUG/.codrug_minimal_done.
    """
    try:
        if os.path.isfile(MIN_MARKER):
            if callback: callback(True, "Already installed.")
            return
        pkgs = need_install_essentials()
        if not pkgs:
            Path(MIN_MARKER).write_text("ok")
            if callback: callback(True, "All essentials present.")
            return
        r = _run([VENV_PY, "-m", "pip", "install", "--no-cache-dir"] + pkgs)
        ok = (r.returncode == 0)
        if ok:
            Path(MIN_MARKER).write_text("ok")
        if callback: callback(ok, r.stdout if r.stdout else "done")
    except Exception as e:
        if callback: callback(False, str(e))

# -------- UI (Splash) --------
class SplashScreen(QWidget):
    check_complete = pyqtSignal(dict)   # emite dicionário de status ao final
    essentials_done = pyqtSignal(bool, str)  # retorno da instalação mínima (thread-safe)

    def __init__(self, dp_dir):
        super().__init__()
        self.dp_dir = dp_dir
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Centralizar
        screen = QGuiApplication.primaryScreen()
        geom = screen.availableGeometry()
        w, h = 520, 320
        self.resize(w, h)
        self.move((geom.width() - w) // 2, (geom.height() - h) // 3)

        # Layout compacto: ícone + barra
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Logo
        logo = QLabel()
        logo_path = os.path.join(self.dp_dir, "ICONS", "CODRUG.png")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo.setPixmap(pix)
        else:
            logo.setText("")
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        # Barra de progresso
        self.progress = QProgressBar()
        self.progress.setAlignment(Qt.AlignCenter)
        self.progress.setFixedHeight(20)
        self.progress.setStyleSheet("QProgressBar { font-size: 11px; border-radius: 5px; }")
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.setLayout(layout)

        # Estado
        self.status = {
            "desktop_ok": False,
            "folders_ok": False,
            "essentials_installed": False,
            "versions": {},
        }

        self.essentials_done.connect(self._on_essentials_done)

        # Controle de progresso suave: valor atual vs. alvo
        self._target = 0
        self._timer = QTimer(self)
        self._timer.setInterval(15)                  # resposta rápida
        self._timer.timeout.connect(self._advance_progress)

    # -------- Public API --------
    def start_checks(self):
        # começa do zero e já mostra progresso animando ao alvo
        self.progress.setValue(0)
        self._target = 5
        self._timer.start()

        # 1) .desktop
        ensure_desktop()
        self.status["desktop_ok"] = True
        self._set_target(25)

        # 2) Estrutura de pastas
        for folder in (f"{self.dp_dir}/JOBS", f"{self.dp_dir}/MODULES", f"{self.dp_dir}/TEST", f"{self.dp_dir}/ICONS"):
            os.makedirs(folder, exist_ok=True)
        self.status["folders_ok"] = True
        self._set_target(50)

        # 3) Versões (importlib.metadata) — não bloqueia se algo faltar
        for name in [
            "matplotlib", "numpy", "pandas", "scipy", "seaborn",
            "chembl_webresource_client", "rdkit", "scikit-learn", "torch", "tensorflow"
        ]:
            ver = _safe_version(name)
            if ver:
                self.status["versions"][name] = ver
        self._set_target(60)

        # 4) Instalação mínima essencial (uma única vez) — thread-safe via sinal
        self._set_target(70)  # alvo intermediário enquanto instala
        def _worker():
            def _cb(ok, log_text):
                try:
                    self.essentials_done.emit(bool(ok), str(log_text or ""))
                except RuntimeError:
                    pass
            install_minimal_essentials(callback=_cb)
        Thread(target=_worker, daemon=True).start()

    # -------- Internals --------
    def _on_essentials_done(self, ok: bool, _log_text: str):
        # Concluiu: leve até 100 e finalize
        self.status["essentials_installed"] = bool(ok)
        self._set_target(100)
        # Quando a barra chegar a 100, _advance_progress chamará _finish

    def _advance_progress(self):
        cur = self.progress.value()
        if cur >= self._target:
            # Se já chegamos no alvo e o alvo é 100, finalizar
            if self._target >= 100:
                self._finish()
            return
        # passo adaptativo para suavizar (não pular de uma vez)
        step = max(1, (self._target - cur) // 10)
        self.progress.setValue(min(cur + step, self._target))

    def _set_target(self, value: int):
        # define novo alvo sem ultrapassar 100
        self._target = max(0, min(100, int(value)))

    def _finish(self):
        if self._timer.isActive():
            self._timer.stop()
        self.progress.setValue(100)
        self.check_complete.emit(self.status)

    # _log mantido no-op (compatibilidade)
    def _log(self, _msg: str):
        return


# Para teste isolado (opcional)
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = SplashScreen(APP_DIR)
    w.show()
    # chame imediatamente para aparecer o quanto antes
    QTimer.singleShot(0, w.start_checks)
    sys.exit(app.exec_())

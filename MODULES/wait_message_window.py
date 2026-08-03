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

"""Janela de espera (texto simples, sem barra de progresso) rodando como um PROCESSO separado.

Motivo: a STEP 6 do CODRUG.py roda seus cálculos de forma síncrona na própria thread da GUI (sem
QThread em background, para evitar os crashes nativos já relatados nessa parte do app). Enquanto o
cálculo está rodando, o processo principal para de responder a eventos do X server/Wayland
compositor por completo — e é o próprio gerenciador de janelas, não o CODRUG, quem decide como
desenhar uma janela "não respondendo": em muitos ambientes Linux isso aparece como conteúdo preto,
sem o texto, até o processo voltar a responder. Não existe ajuste de estilo, cor ou frequência de
'processEvents()' dentro do MESMO processo bloqueado que resolva isso — a única forma é rodar essa
janela de aviso em um processo do sistema operacional à parte, com seu próprio event loop, que
continua respondendo/pintando normalmente independente do que o processo principal esteja fazendo
(mesmo padrão já usado por MODULES/hw_monitor_window.py para o monitor de CPU/GPU).

Uso: python3 wait_message_window.py "<título>" "<mensagem>"
"""

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout


def main():
    title = sys.argv[1] if len(sys.argv) > 1 else "Wait"
    message = sys.argv[2] if len(sys.argv) > 2 else "Please wait for it to finish!"

    app = QApplication(sys.argv)

    dlg = QDialog(None)
    dlg.setWindowTitle(title)
    dlg.setWindowModality(Qt.ApplicationModal)
    dlg.setStyleSheet("QDialog { background-color: #0D1B2A; }")

    layout = QVBoxLayout(dlg)
    label = QLabel(message)
    label.setAlignment(Qt.AlignCenter)
    label.setWordWrap(True)
    label.setStyleSheet("padding: 24px; font-size: 11pt; color: #C9D1D9; background-color: transparent;")
    layout.addWidget(label)

    dlg.setMinimumWidth(360)
    dlg.show()
    dlg.raise_()
    dlg.activateWindow()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

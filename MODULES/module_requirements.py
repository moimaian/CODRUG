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
import shutil
import urllib.request
import threading
import importlib
import importlib.util
import platform
import re
from pathlib import Path
from typing import Any, Optional, List, cast

try:
    import MODULES.i18n as i18n
except ImportError:
    # Ocorre quando este arquivo é executado diretamente de dentro de MODULES/ (bloco
    # "For direct test" no fim do arquivo) em vez de importado a partir da raiz do projeto -
    # adiciona a raiz do projeto (pai de MODULES/) ao sys.path e tenta de novo.
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import MODULES.i18n as i18n

TARGET_VENV_PYTHON = "3.10.12"
PYENV_APT_BUILD_DEPS = [
    "build-essential",
    "libssl-dev",
    "zlib1g-dev",
    "libbz2-dev",
    "libreadline-dev",
    "libsqlite3-dev",
    "curl",
    "git",
    "libncursesw5-dev",
    "xz-utils",
    "tk-dev",
    "libxml2-dev",
    "libxmlsec1-dev",
    "libffi-dev",
    "liblzma-dev",
]

_PYQT_IMPORT_ERROR = None
pyqtSignal = cast(Any, None)
try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QLabel, QCheckBox, QPushButton,
        QTextEdit, QApplication, QHBoxLayout, QMessageBox, QProgressBar, QLineEdit, QGridLayout,
        QRadioButton, QButtonGroup
    )
    from PyQt5.QtCore import Qt, pyqtSignal as _pyqtSignal
    pyqtSignal = _pyqtSignal
    _PYQT_AVAILABLE = True
except Exception as exc:
    _PYQT_IMPORT_ERROR = exc
    _PYQT_AVAILABLE = False

    class _DummySignal:
        def connect(self, *args, **kwargs):
            return None

        def emit(self, *args, **kwargs):
            return None

    pyqtSignal = cast(Any, lambda *args, **kwargs: _DummySignal())

    class _DummyQt:
        ApplicationModal = 0
        AlignCenter = 0
        AlignLeft = 0
        RichText = 0

    class _DummyWidget:
        def __init__(self, *args: Any, **kwargs: Any):
            pass

        def __getattr__(self, name: str) -> Any:
            def _dummy(*args: Any, **kwargs: Any) -> Any:
                return None
            return _dummy

    Qt = cast(Any, _DummyQt())
    QWidget = cast(Any, _DummyWidget)
    QVBoxLayout = QLabel = QCheckBox = QPushButton = QTextEdit = QApplication = cast(Any, _DummyWidget)
    QHBoxLayout = QMessageBox = QProgressBar = QLineEdit = QGridLayout = cast(Any, _DummyWidget)
    QRadioButton = QButtonGroup = cast(Any, _DummyWidget)

_SS_BTN_DANGER = """
QPushButton {
    background: #4A2A2A;
    color: #F39A8A;
    font-weight: bold;
    border: 1px solid #F39A8A;
    border-radius: 5px;
    padding: 6px 16px;
}
QPushButton:hover { background: #F0AA9D; color: #0D1B2A; }
QPushButton:pressed { background: #D98979; color: #FFF; }
QPushButton:disabled { background: #352323; color: #8D6A66; border-color: #5A4340; }
"""

_SS_BTN_PRIMARY = """
QPushButton {
    background: #1A4A30;
    color: #2ECC71;
    font-weight: bold;
    border: 1px solid #2ECC71;
    border-radius: 5px;
    padding: 6px 16px;
}
QPushButton:hover { background: #27AE60; color: #0D1B2A; }
QPushButton:pressed { background: #1E8449; color: #FFF; }
QPushButton:disabled { background: #1C2E20; color: #3D6B4A; border-color: #2A4A36; }
"""

# role="secondary" (cinza), mesma paleta usada em CODRUG.py para botões secundários.
_SS_BTN_SECONDARY = """
QPushButton {
    background: #243746;
    color: #A9BED1;
    font-weight: bold;
    border: 1px solid #6E8CA8;
    border-radius: 5px;
    padding: 6px 16px;
}
QPushButton:hover { background: #37536C; color: #C9D1D9; }
QPushButton:pressed { background: #1C3249; color: #FFF; }
QPushButton:disabled { background: #1B2730; color: #4F6577; border-color: #344654; }
"""

# Mesma altura/fonte dos botões acima, só com o padding horizontal reduzido pela
# metade (16px -> 8px) para deixar os botões "Instalar Selecionados" / "Fechar"
# desta janela mais estreitos, sem mexer na altura nem no texto.
_SS_BTN_DANGER_NARROW = _SS_BTN_DANGER.replace("padding: 6px 16px;", "padding: 6px 8px;")
_SS_BTN_PRIMARY_NARROW = _SS_BTN_PRIMARY.replace("padding: 6px 16px;", "padding: 6px 8px;")
# --------------------------- helpers ---------------------------

def _run(cmd: list, check=False, env=None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=check, env=env)

def _run_interactive(cmd: list[str]) -> int:
    proc = subprocess.run(cmd)
    return proc.returncode

def _which(p: str) -> Optional[str]:
    return shutil.which(p)

def _pkg_installed(import_name: str) -> bool:
    return importlib.util.find_spec(import_name) is not None

def _pkg_version(import_name: str) -> Optional[str]:
    try:
        mod = importlib.import_module(import_name)
        return getattr(mod, "__version__", None)
    except Exception:
        return None

def venv_paths(env_name="CODRUG"):
    """
    Define o local do venv do CODRUG e retorna caminhos úteis.
    """
    home = str(Path.home())
    app_dir = os.path.join(home, "CODRUG")
    venv_dir = os.path.join(home, ".venv", "CODRUG")
    py = os.path.join(venv_dir, "bin", "python")
    pip = os.path.join(venv_dir, "bin", "pip")
    return {"app_dir": app_dir, "venv_dir": venv_dir, "python": py, "pip": pip}

def _ensure_pyenv_linux(home: str) -> str:
    """
    Garante pyenv em ~/.pyenv (modo simples, Linux/Mac). Retorna caminho base (~/.pyenv).
    Não mexe em .bashrc; apenas instala se não existir.
    """
    pyenv_root = os.path.join(home, ".pyenv")
    if not os.path.isdir(pyenv_root):
        # instalação mínima via git (mais estável que curl aqui)
        res = _run(["git", "clone", "https://github.com/pyenv/pyenv.git", pyenv_root])
        if res.returncode != 0:
            raise RuntimeError(f"Falha ao clonar pyenv: {res.stdout}")
    return pyenv_root

def _os_release_text() -> str:
    try:
        return Path("/etc/os-release").read_text(encoding="utf-8").lower()
    except Exception:
        return ""

def _supports_apt_bootstrap() -> bool:
    if sys.platform != "linux":
        return False
    if not _which("apt") or not _which("sudo"):
        return False
    os_release = _os_release_text()
    return any(token in os_release for token in ("ubuntu", "debian", "mint", "pop", "zorin"))

def _prompt_yes_no(message: str, default_yes: bool = True) -> bool:
    suffix = "[S/n]" if default_yes else "[s/N]"
    try:
        resp = input(f"{message} {suffix}: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    if not resp:
        return default_yes
    return resp not in ("n", "nao", "não", "no")

def _maybe_install_pyenv_build_deps() -> None:
    if not _supports_apt_bootstrap():
        return
    print("[CODRUG] Python 3.10.12 será provisionado via pyenv.")
    if not _prompt_yes_no("[CODRUG] Deseja instalar automaticamente as dependências de build via apt?", default_yes=True):
        return

    print("[CODRUG] Instalando dependências do sistema para compilar Python 3.10.12...")
    if _run_interactive(["sudo", "apt", "update"]) != 0:
        raise RuntimeError("Falha ao executar 'sudo apt update'.")

    install_cmd = ["sudo", "apt", "install", "-y"] + PYENV_APT_BUILD_DEPS
    if _run_interactive(install_cmd) != 0:
        raise RuntimeError("Falha ao instalar dependências de build do Python 3.10.12 via apt.")

def _pyenv_python_bin(version: str) -> str:
    return os.path.join(str(Path.home()), ".pyenv", "versions", version, "bin", "python")

def ensure_python310_with_pyenv(version: str = TARGET_VENV_PYTHON) -> str:
    """
    Garante que Python <version> está instalado via pyenv e retorna o caminho do binário.
    """
    home = str(Path.home())
    pyenv_root = _ensure_pyenv_linux(home)

    target_py = _pyenv_python_bin(version)
    if not os.path.isfile(target_py):
        _maybe_install_pyenv_build_deps()

        # preparar ambiente para pyenv (apenas para o processo atual)
        env = os.environ.copy()
        env["PYENV_ROOT"] = pyenv_root
        env["PATH"] = os.path.join(pyenv_root, "bin") + os.pathsep + env.get("PATH", "")

        res = _run(["bash", "-lc", f'eval "$(pyenv init -)"; pyenv install -s {version}'], env=env)
        if res.returncode != 0:
            raise RuntimeError(
                "Falha ao instalar Python 3.10.12 via pyenv.\n"
                "Em Debian/Ubuntu, tente manualmente:\n"
                "  sudo apt update\n"
                "  sudo apt install -y " + " ".join(PYENV_APT_BUILD_DEPS) + "\n"
                "Depois execute o CODRUG novamente.\n\n"
                f"Saída do pyenv:\n{res.stdout}"
            )

    # usa o binário recem-instalado
    return target_py if os.path.isfile(target_py) else _pyenv_python_bin(version)

def _python_version_string(pybin: str) -> Optional[str]:
    res = _run([pybin, "-c", "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}')"])
    if res.returncode != 0:
        return None
    return res.stdout.strip() or None

def _is_target_python(pybin: str, version: str = TARGET_VENV_PYTHON) -> bool:
    return _python_version_string(pybin) == version

def _pick_python_for_venv() -> str:
    """
    Retorna um binário de Python 3.10.12 para criar o venv do CODRUG.
    - Se o Python atual for exatamente 3.10.12, usa-o.
    - Se houver um python3.10 exatamente 3.10.12 no PATH, usa-o.
    - Caso contrário, garante via pyenv (3.10.12) e usa esse.
    """
    if _is_target_python(sys.executable):
        return sys.executable
    cand = _which("python3.10")
    if cand and _is_target_python(cand):
        return cand
    return ensure_python310_with_pyenv(TARGET_VENV_PYTHON)

def ensure_venv(env_name="CODRUG") -> dict:
    p = venv_paths(env_name)
    os.makedirs(p["app_dir"], exist_ok=True)

    recreate_venv = False
    if os.path.isdir(p["venv_dir"]) and os.path.isfile(p["python"]):
        recreate_venv = not _is_target_python(p["python"])

    if recreate_venv and os.path.isdir(p["venv_dir"]):
        shutil.rmtree(p["venv_dir"], ignore_errors=True)

    if recreate_venv or not os.path.isdir(p["venv_dir"]) or not os.path.isfile(p["python"]):
        py_for_venv = _pick_python_for_venv()
        # cria o venv
        res = _run([py_for_venv, "-m", "venv", p["venv_dir"]])
        if res.returncode != 0:
            raise RuntimeError(f"Falha ao criar venv: {res.stdout}")
        _run([p["python"], "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])

    current_venv_version = _python_version_string(p["python"])
    if current_venv_version != TARGET_VENV_PYTHON:
        raise RuntimeError(
            f"O venv {p['venv_dir']} foi criado com Python {current_venv_version or 'desconhecido'}, "
            f"mas o CODRUG exige Python {TARGET_VENV_PYTHON}."
        )

    return p

def _has_module(pybin: str, module_name: str) -> bool:
    res = _run([pybin, "-c", f"import {module_name}"])
    return res.returncode == 0

def _running_in_target_venv(env_name: str = "CODRUG") -> bool:
    try:
        return Path(sys.executable).resolve() == Path(venv_paths(env_name)["python"]).resolve()
    except Exception:
        return False

def ensure_bootstrap_packages(env_name="CODRUG", packages: Optional[dict] = None) -> tuple[dict, bool]:
    """
    Garante no venv um conjunto mínimo de pacotes necessários para a UI iniciar.
    Retorna (paths, installed_any).
    """
    p = ensure_venv(env_name)
    bootstrap_packages = packages or {"PyQt5": "PyQt5>=5.15,<5.16"}
    missing_specs = [spec for module_name, spec in bootstrap_packages.items() if not _has_module(p["python"], module_name)]
    if not missing_specs:
        return p, False

    cmd = [p["python"], "-m", "pip", "install", "--upgrade"] + missing_specs
    res = _run(cmd)
    if res.returncode != 0:
        raise RuntimeError(f"Falha ao instalar dependências mínimas do bootstrap: {res.stdout}")
    return p, True

def bootstrap_pyqt5(interactive: bool = True, reexec: bool = False, env_name: str = "CODRUG") -> bool:
    """
    Garante que o venv do CODRUG exista, que use Python 3.10+ e que PyQt5 esteja instalado.
    Quando reexec=True, reinicia o processo com o Python do venv para que a UI já nasça no ambiente correto.
    """
    if os.environ.get("CODRUG_VENV_ACTIVE") == "1" and _running_in_target_venv(env_name):
        return True

    target_paths = venv_paths(env_name)
    target_python = target_paths["python"]

    if interactive and not _running_in_target_venv(env_name):
        print("\n" + "═" * 62)
        print("  CODRUG — Configuração do Ambiente")
        print("═" * 62)
        print(f"  Python atual   : {sys.executable}")
        print(f"  Versão Python  : {sys.version.split()[0]}")
        print(f"  Ambiente alvo  : {target_paths['venv_dir']}")
        print(f"  Python alvo    : {TARGET_VENV_PYTHON}")
        if os.path.isdir(target_paths["venv_dir"]) and os.path.isfile(target_python):
            print("  Status         : ✔ venv já existe")
        else:
            print("  Status         : ○ venv será criado agora")
        print()
        print("  O CODRUG utiliza um ambiente virtual isolado (~/.venv/CODRUG)")
        print("  com Python 3.10.12 para manter compatibilidade com RDKit e outras dependências.")
        print()
        try:
            resp = input("  Deseja continuar? [S/n]: ").strip().lower()
            if resp in ("n", "nao", "não", "no"):
                print("\n[CODRUG] Cancelado pelo usuário.")
                return False
        except (EOFError, KeyboardInterrupt):
            print("\n[CODRUG] Cancelado.")
            return False

    p = ensure_venv(env_name)
    venv_version = _python_version_string(p["python"])
    if venv_version != TARGET_VENV_PYTHON:
        print(
            f"[CODRUG] ❌ O ambiente virtual não está usando Python {TARGET_VENV_PYTHON}. "
            f"Versão detectada: {venv_version or 'desconhecida'}."
        )
        print("[CODRUG] Instale o Python 3.10.12 e recrie ~/.venv/CODRUG antes de continuar.")
        return False

    print(f"[CODRUG] ✅ Venv em {p['venv_dir']} usando Python {venv_version}.")
    installed_pyqt = False
    if not _has_module(p["python"], "PyQt5"):
        print("[CODRUG] Instalando PyQt5 no venv...")
        res = _run([p["python"], "-m", "pip", "install", "--upgrade", "PyQt5>=5.15,<5.16"])
        if res.returncode != 0:
            lines = [l for l in res.stdout.splitlines() if any(k in l for k in ("ERROR", "error", "Failed"))]
            print("[CODRUG] ❌ Falha ao instalar PyQt5:")
            for line in lines[:5]:
                print(f"   {line}")
            return False
        print("[CODRUG] ✅ PyQt5 instalado no venv.")
        installed_pyqt = True
    else:
        print("[CODRUG] ✅ PyQt5 já disponível no venv.")

    if reexec:
        current_py = os.path.realpath(sys.executable)
        target_py = os.path.realpath(p["python"])
        if installed_pyqt or current_py != target_py:
            env = os.environ.copy()
            env["CODRUG_VENV_ACTIVE"] = "1"
            print(f"\n[CODRUG] Reiniciando com o Python do venv...")
            print(f"         {p['python']}\n")
            os.execve(p["python"], [p["python"]] + sys.argv, env)

    return True

def detect_python() -> dict:
    ver = sys.version_info
    version_str = f"{ver.major}.{ver.minor}.{ver.micro}"
    ok = ver >= (3, 10)
    return {
        "version": version_str,
        "ok": ok,
        "msg": version_str if ok else f"Python {version_str} — necessário >= 3.10",
    }

def detect_cpu() -> dict:
    info = {
        "brand": platform.processor() or "Desconhecido",
        "arch": platform.machine(),
        "cores_logical": os.cpu_count() or 1,
        "cores_physical": 1,
    }
    try:
        if platform.system() == "Linux":
            out = subprocess.check_output(["lscpu"], text=True, stderr=subprocess.DEVNULL)
            for line in out.splitlines():
                if "Core(s) per socket" in line:
                    cores = int(line.split(":")[1].strip())
                    sockets_lines = [l for l in out.splitlines() if "Socket(s)" in l]
                    sockets = int(sockets_lines[0].split(":")[1].strip()) if sockets_lines else 1
                    info["cores_physical"] = cores * sockets
                if "Model name" in line:
                    info["brand"] = line.split(":", 1)[1].strip()
    except Exception:
        info["cores_physical"] = max(1, info["cores_logical"] // 2)
    return info

def detect_gpu() -> dict:
    result = {
        "available": False,
        "name": None,
        "vram_gb": 0,
        "driver_version": None,
        "cuda_version": None,
        "cuda_major": 0,
        "cuda_minor": 0,
    }
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader,nounits"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip().splitlines()[0]
        parts = [p.strip() for p in out.split(",")]
        result.update({
            "available": True,
            "name": parts[0],
            "vram_gb": round(int(parts[1]) / 1024, 1),
            "driver_version": parts[2],
        })
    except Exception:
        return result

    try:
        nvcc_out = subprocess.check_output(["nvcc", "--version"], text=True, stderr=subprocess.DEVNULL)
        match = re.search(r"release (\d+)\.(\d+)", nvcc_out)
        if match:
            result["cuda_major"] = int(match.group(1))
            result["cuda_minor"] = int(match.group(2))
            result["cuda_version"] = f"{result['cuda_major']}.{result['cuda_minor']}"
    except Exception:
        try:
            major = int(result["driver_version"].split(".")[0])
            if major >= 570:
                result["cuda_major"], result["cuda_minor"] = 12, 8
            elif major >= 545:
                result["cuda_major"], result["cuda_minor"] = 12, 3
            elif major >= 530:
                result["cuda_major"], result["cuda_minor"] = 12, 1
            elif major >= 520:
                result["cuda_major"], result["cuda_minor"] = 11, 8
            if result["cuda_major"]:
                result["cuda_version"] = f"{result['cuda_major']}.{result['cuda_minor']}"
                result["cuda_inferred"] = True
        except Exception:
            pass
    return result

def detect_ram() -> dict:
    try:
        if platform.system() == "Linux":
            with open("/proc/meminfo", "r", encoding="utf-8") as handle:
                mem = {}
                for line in handle:
                    parts = line.split()
                    if len(parts) >= 2:
                        mem[parts[0].rstrip(":")] = int(parts[1])
            total_gb = round(mem.get("MemTotal", 0) / 1e6, 1)
            free_gb = round(mem.get("MemAvailable", 0) / 1e6, 1)
            return {"total_gb": total_gb, "free_gb": free_gb, "ok": total_gb >= 8}
    except Exception:
        pass
    return {"total_gb": 0, "free_gb": 0, "ok": True}

def detect_disk(path: Optional[str] = None) -> dict:
    path = path or str(Path.home())
    try:
        stat = shutil.disk_usage(path)
        return {
            "total_gb": round(stat.total / 1e9, 1),
            "free_gb": round(stat.free / 1e9, 1),
            "ok": stat.free / 1e9 >= 10,
        }
    except Exception:
        return {"total_gb": 0, "free_gb": 0, "ok": False}

def detect_hardware() -> dict:
    return {
        "python": detect_python(),
        "cpu": detect_cpu(),
        "gpu": detect_gpu(),
        "ram": detect_ram(),
        "disk": detect_disk(),
    }

def select_torch_variant(gpu: dict) -> dict:
    cuda = gpu.get("cuda_major", 0)
    minor = gpu.get("cuda_minor", 0)
    if gpu.get("available") and cuda >= 12:
        if minor >= 6:
            return {"index_url": "https://download.pytorch.org/whl/cu128", "tag": "cu128", "version": "2.7.0"}
        return {"index_url": "https://download.pytorch.org/whl/cu121", "tag": "cu121", "version": "2.5.1"}
    if gpu.get("available") and cuda == 11:
        return {"index_url": "https://download.pytorch.org/whl/cu118", "tag": "cu118", "version": "2.4.0"}
    return {"index_url": "https://download.pytorch.org/whl/cpu", "tag": "cpu", "version": "2.7.0"}

def select_cuml_variant(gpu: dict) -> dict:
    """
    RAPIDS cuML ships pip wheels (cuml-cu11 / cuml-cu12) for Linux + NVIDIA GPU
    (Volta or newer, CUDA 11.4+/12.x) only. It is the actual soft dependency
    PyCaret warns about when a GPU-accelerated estimator is requested
    (use_gpu=True/Auto). See: https://docs.rapids.ai/install
    """
    cuda = gpu.get("cuda_major", 0)
    if platform.system() != "Linux":
        return {"available": False, "pkg": None, "reason": "cuML pip wheels are Linux-only."}
    if not gpu.get("available") or cuda < 11:
        return {"available": False, "pkg": None, "reason": "No compatible NVIDIA GPU/CUDA (>=11) detected."}
    pkg = "cuml-cu12" if cuda >= 12 else "cuml-cu11"
    return {"available": True, "pkg": pkg, "reason": None}

def recommend_installer_defaults(hw: Optional[dict] = None) -> dict:
    hw = hw or detect_hardware()
    torch_info = select_torch_variant(hw["gpu"])
    cuml_info = select_cuml_variant(hw["gpu"])
    return {
        "python_version": "3.10.12",
        "java_version": "11",
        "scikitlearn_version": "1.4.2",
        "pycaret_version": "3.3.2",
        "chembl_version": "0.10.9",
        "padelpy_version": "0.1.13",
        "rdkit_version": "2022.9.5",
        "matplotlib_version": "3.7.5",
        "seaborn_version": "0.13.2",
        "joblib_version": "1.3.2",
        "pandas_version": "2.1.4",
        "numpy_version": "1.26.4",
        "tensorflow_version": "2.15.*",
        "pytorch_variant": torch_info["tag"],
        "pytorch_version": torch_info["version"],
        "pytorch_index_url": torch_info["index_url"],
        "cuml_pkg": cuml_info["pkg"] or "cuml-cu12",
        "cuml_version": "",
        "cuml_available": cuml_info["available"],
        "cuml_reason": cuml_info["reason"],
    }

def _pip_install(python_bin: str, pkgs: List[str]) -> subprocess.CompletedProcess:
    """
    Executa pip install no venv (python -m pip install ...).
    """
    cmd = [python_bin, "-m", "pip", "install"] + pkgs
    return _run(cmd)

# --------------------------- UI ---------------------------

class RequirementsInstaller(cast(Any, QWidget)):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    enable_install_signal = pyqtSignal(bool)

    def __init__(self, parent=None, idioma="en"):
        if not _PYQT_AVAILABLE:
            raise RuntimeError(f"PyQt5 is required to open RequirementsInstaller: {_PYQT_IMPORT_ERROR}")
        super().__init__(parent)
        # Traduzido uma única vez, na construção, a partir do idioma passado pelo chamador (self._idioma
        # do CODRUG.MainWindow) - esta janela não tem bandeiras próprias de troca de idioma.
        self._idioma = idioma if idioma in ("en", "pt") else "en"
        self.setWindowTitle(i18n.t("req_window_title", self._idioma))
        self.setMinimumWidth(680)

        layout = QVBoxLayout()
        self._hw = detect_hardware()
        self._defaults = recommend_installer_defaults(self._hw)
        self._version_groups: list = []

        env_info = QLabel(
            i18n.t(
                "req_env_info", self._idioma,
                python_exe=sys.executable,
                python_ver=sys.version.split()[0],
            )
        )
        layout.addWidget(env_info)

        # Default versions (editable)
        self.python_version = self._defaults["python_version"]
        self.java_version = self._defaults["java_version"]
        self.scikitlearn_version = self._defaults["scikitlearn_version"]
        self.pycaret_version = self._defaults["pycaret_version"]
        self.chembl_version = self._defaults["chembl_version"]
        self.padelpy_version = self._defaults["padelpy_version"]
        self.rdkit_version = self._defaults["rdkit_version"]
        self.matplotlib_version = self._defaults["matplotlib_version"]
        self.seaborn_version = self._defaults["seaborn_version"]
        self.joblib_version = self._defaults["joblib_version"]
        self.pandas_version = self._defaults["pandas_version"]
        self.numpy_version = self._defaults["numpy_version"]
        self.pytorch_version = self._defaults["pytorch_version"]
        self.pytorch_cuda_variant = self._defaults["pytorch_variant"]
        self.pytorch_index_url = self._defaults["pytorch_index_url"]
        self.tensorflow_version = self._defaults["tensorflow_version"]
        self.cuml_pkg = self._defaults["cuml_pkg"]
        self.cuml_version = self._defaults["cuml_version"]
        self.cuml_available = self._defaults["cuml_available"]

        gL_widget = QWidget(); gL = QGridLayout(gL_widget)

        # Row 0..N
        self.check_venv = QCheckBox(i18n.t("req_chk_venv", self._idioma))
        self.ed_python_version = QLineEdit(); self.ed_python_version.setText(self.python_version)
        self.ed_python_version.setToolTip(i18n.t("req_tooltip_venv", self._idioma))

        self.check_java = QCheckBox(i18n.t("req_chk_java", self._idioma))
        self.rb_java_default = QRadioButton(i18n.t("req_java_default_label", self._idioma))
        self.rb_java_version = QRadioButton(i18n.t("req_java_version_label", self._idioma))
        self.rb_java_version.setChecked(True)
        self.java_version_group = QButtonGroup(self)
        self.java_version_group.addButton(self.rb_java_default)
        self.java_version_group.addButton(self.rb_java_version)
        self.ed_java_version = QLineEdit(); self.ed_java_version.setText(self.java_version)
        self.ed_java_version.setToolTip(i18n.t("req_tooltip_java_version", self._idioma))
        self.rb_java_default.toggled.connect(lambda checked: self.ed_java_version.setEnabled(not checked))
        java_box = QWidget(); java_row = QHBoxLayout(java_box); java_row.setContentsMargins(0, 0, 0, 0)
        java_row.addWidget(self.rb_java_default)
        java_row.addWidget(self.rb_java_version)
        java_row.addWidget(self.ed_java_version)

        self.check_scikitlearn = QCheckBox(i18n.t("req_chk_scikitlearn", self._idioma))
        scikitlearn_box, self.rb_scikitlearn_latest, self.rb_scikitlearn_version, self.ed_scikitlearn_version = \
            self._make_version_row(self.scikitlearn_version)

        self.check_pycaret = QCheckBox(i18n.t("req_chk_pycaret", self._idioma))
        pycaret_box, self.rb_pycaret_latest, self.rb_pycaret_version, self.ed_pycaret_version = \
            self._make_version_row(self.pycaret_version)

        self.check_cuml = QCheckBox(i18n.t("req_chk_cuml", self._idioma))
        cuml_box, self.rb_cuml_latest, self.rb_cuml_version, self.ed_cuml_version = \
            self._make_version_row(self.cuml_version)
        self.ed_cuml_version.setPlaceholderText(i18n.t("req_placeholder_cuml_version", self._idioma, pkg=self.cuml_pkg))
        if not self.cuml_available:
            self.check_cuml.setEnabled(False)
            self.check_cuml.setToolTip(
                i18n.t("req_tooltip_cuml_unavailable", self._idioma, reason=self._defaults['cuml_reason'])
            )

        self.check_chembl = QCheckBox(i18n.t("req_chk_chembl", self._idioma))
        chembl_box, self.rb_chembl_latest, self.rb_chembl_version, self.ed_chembl_version = \
            self._make_version_row(self.chembl_version)

        self.check_padelpy = QCheckBox(i18n.t("req_chk_padelpy", self._idioma))
        padelpy_box, self.rb_padelpy_latest, self.rb_padelpy_version, self.ed_padelpy_version = \
            self._make_version_row(self.padelpy_version)

        self.check_rdkit = QCheckBox(i18n.t("req_chk_rdkit", self._idioma))
        rdkit_box, self.rb_rdkit_latest, self.rb_rdkit_version, self.ed_rdkit_version = \
            self._make_version_row(self.rdkit_version)

        self.check_matplotlib = QCheckBox(i18n.t("req_chk_matplotlib", self._idioma))
        matplotlib_box, self.rb_matplotlib_latest, self.rb_matplotlib_version, self.ed_matplotlib_version = \
            self._make_version_row(self.matplotlib_version)

        self.check_seaborn = QCheckBox(i18n.t("req_chk_seaborn", self._idioma))
        seaborn_box, self.rb_seaborn_latest, self.rb_seaborn_version, self.ed_seaborn_version = \
            self._make_version_row(self.seaborn_version)

        self.check_joblib = QCheckBox(i18n.t("req_chk_joblib", self._idioma))
        joblib_box, self.rb_joblib_latest, self.rb_joblib_version, self.ed_joblib_version = \
            self._make_version_row(self.joblib_version)

        self.check_pandas = QCheckBox(i18n.t("req_chk_pandas", self._idioma))
        pandas_box, self.rb_pandas_latest, self.rb_pandas_version, self.ed_pandas_version = \
            self._make_version_row(self.pandas_version)

        self.check_numpy = QCheckBox(i18n.t("req_chk_numpy", self._idioma))
        numpy_box, self.rb_numpy_latest, self.rb_numpy_version, self.ed_numpy_version = \
            self._make_version_row(self.numpy_version)

        # PyTorch / TensorFlow
        self.check_pytorch = QCheckBox(i18n.t("req_chk_pytorch", self._idioma))
        self.ed_pytorch_variant = QLineEdit(); self.ed_pytorch_variant.setText(self.pytorch_cuda_variant)
        pytorch_version_box, self.rb_pytorch_latest, self.rb_pytorch_version, self.ed_pytorch_version = \
            self._make_version_row(self.pytorch_version)
        self.ed_pytorch_index = QLineEdit(); self.ed_pytorch_index.setText(self.pytorch_index_url)
        pytorch_box = QWidget(); pytorch_row = QHBoxLayout(pytorch_box); pytorch_row.setContentsMargins(0,0,0,0)
        pytorch_row.addWidget(self.ed_pytorch_variant); pytorch_row.addWidget(pytorch_version_box); pytorch_row.addWidget(self.ed_pytorch_index)

        self.check_tensorflow = QCheckBox(i18n.t("req_chk_tensorflow", self._idioma))
        tensorflow_box, self.rb_tensorflow_latest, self.rb_tensorflow_version, self.ed_tensorflow_version = \
            self._make_version_row(self.tensorflow_version)

        self.check_libs = QCheckBox(i18n.t("req_chk_libs", self._idioma))
        self.ed_libs_version = QLineEdit(); self.ed_libs_version.setPlaceholderText(i18n.t("req_placeholder_libs_version", self._idioma))

        r = 0
        gL.addWidget(self.check_venv, r, 0); gL.addWidget(self.ed_python_version, r, 1); r += 1
        gL.addWidget(self.check_java, r, 0); gL.addWidget(java_box, r, 1); r += 1
        gL.addWidget(self.check_scikitlearn, r, 0); gL.addWidget(scikitlearn_box, r, 1); r += 1
        gL.addWidget(self.check_pycaret, r, 0); gL.addWidget(pycaret_box, r, 1); r += 1
        gL.addWidget(self.check_cuml, r, 0); gL.addWidget(cuml_box, r, 1); r += 1
        gL.addWidget(self.check_chembl, r, 0); gL.addWidget(chembl_box, r, 1); r += 1
        gL.addWidget(self.check_padelpy, r, 0); gL.addWidget(padelpy_box, r, 1); r += 1
        gL.addWidget(self.check_rdkit, r, 0); gL.addWidget(rdkit_box, r, 1); r += 1
        gL.addWidget(self.check_matplotlib, r, 0); gL.addWidget(matplotlib_box, r, 1); r += 1
        gL.addWidget(self.check_seaborn, r, 0); gL.addWidget(seaborn_box, r, 1); r += 1
        gL.addWidget(self.check_joblib, r, 0); gL.addWidget(joblib_box, r, 1); r += 1
        gL.addWidget(self.check_pandas, r, 0); gL.addWidget(pandas_box, r, 1); r += 1
        gL.addWidget(self.check_numpy, r, 0); gL.addWidget(numpy_box, r, 1); r += 1

        gL.addWidget(self.check_pytorch, r, 0); gL.addWidget(pytorch_box, r, 1); r += 1
        gL.addWidget(self.check_tensorflow, r, 0); gL.addWidget(tensorflow_box, r, 1); r += 1

        gL.addWidget(self.check_libs, r, 0); r += 1

        gL.setColumnStretch(0, 2); gL.setColumnStretch(1, 1)
        layout.addWidget(gL_widget)

        # Progress & log
        self.progress = QProgressBar(); self.progress.setValue(0)
        layout.addWidget(self.progress)
        self.log = QTextEdit(); self.log.setReadOnly(True)
        layout.addWidget(self.log)

        btns = QHBoxLayout()
        btns.addStretch(1)
        self.btn_select_all = QPushButton(i18n.t("req_btn_select_all", self._idioma))
        self.btn_select_all.setProperty("role", "secondary")
        self.btn_select_all.setStyleSheet(_SS_BTN_SECONDARY)
        self.btn_select_all.clicked.connect(self.select_all)
        btns.addWidget(self.btn_select_all)
        self.btn_install = QPushButton(i18n.t("req_btn_install_selected", self._idioma)); self.btn_install.clicked.connect(self.start_installation)
        self.btn_install.setStyleSheet(_SS_BTN_PRIMARY_NARROW)
        btns.addWidget(self.btn_install)
        self.btn_close = QPushButton(i18n.t("req_btn_close", self._idioma))
        self.btn_close.setProperty("role", "danger")
        self.btn_close.setStyleSheet(_SS_BTN_DANGER_NARROW)
        self.btn_close.clicked.connect(self.close)
        btns.addWidget(self.btn_close)
        btns.addStretch(1)
        layout.addLayout(btns)

        self.setLayout(layout)
        self.thread = None
        self.log_signal.connect(self._log)
        self.progress_signal.connect(self._set_progress)
        self.enable_install_signal.connect(self._set_install_enabled)

    # --------------------------- widget helpers ---------------------------

    def _make_version_row(self, tested_version: str):
        """
        Cria o par de opções "instalar mais recente" vs. "instalar versão já
        testada" (mesma lógica usada para o Java), com a versão testada marcada
        por padrão. Quando não há versão testada curada (string vazia), a opção
        "mais recente" começa marcada.
        Retorna (box_widget, rb_latest, rb_tested, ed_version).
        """
        rb_latest = QRadioButton(i18n.t("req_opt_latest", self._idioma))
        rb_tested = QRadioButton(i18n.t("req_opt_tested", self._idioma))
        group = QButtonGroup(self)
        group.addButton(rb_latest)
        group.addButton(rb_tested)
        self._version_groups.append(group)

        ed_version = QLineEdit(); ed_version.setText(tested_version)
        use_latest = not tested_version
        rb_latest.setChecked(use_latest)
        rb_tested.setChecked(not use_latest)
        ed_version.setEnabled(not use_latest)
        rb_latest.toggled.connect(lambda checked: ed_version.setEnabled(not checked))

        box = QWidget(); row = QHBoxLayout(box); row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(rb_latest); row.addWidget(rb_tested); row.addWidget(ed_version)
        return box, rb_latest, rb_tested, ed_version

    def _version_spec(self, pkgname: str, rb_latest: "QRadioButton", version: str) -> str:
        """
        Monta o especificador de instalação pip: sem pin de versão quando
        "mais recente" está selecionado (ou não há versão preenchida), com
        pin (pkg==version) caso contrário.
        """
        version = (version or "").strip()
        if rb_latest.isChecked() or not version:
            return pkgname
        return f"{pkgname}=={version}"

    # --------------------------- actions ---------------------------

    def select_all(self):
        """
        Alterna entre marcar e desmarcar todas as checkboxes habilitadas: se todas já
        estiverem marcadas, o clique desmarca; caso contrário (nenhuma ou algumas
        marcadas), o clique marca todas.
        """
        checkboxes = [
            self.check_venv, self.check_java, self.check_scikitlearn, self.check_pycaret,
            self.check_cuml, self.check_chembl, self.check_padelpy, self.check_rdkit,
            self.check_matplotlib, self.check_seaborn, self.check_joblib, self.check_pandas,
            self.check_numpy, self.check_pytorch, self.check_tensorflow, self.check_libs,
        ]
        enabled = [chk for chk in checkboxes if chk.isEnabled()]
        all_checked = bool(enabled) and all(chk.isChecked() for chk in enabled)
        for chk in enabled:
            chk.setChecked(not all_checked)

    def start_installation(self):
        self.btn_install.setEnabled(False)
        self.progress.setValue(0)

        # update from UI
        self.java_version        = self.ed_java_version.text().strip() or self._defaults["java_version"]
        self.scikitlearn_version = self.ed_scikitlearn_version.text().strip()
        self.pycaret_version     = self.ed_pycaret_version.text().strip()
        self.chembl_version      = self.ed_chembl_version.text().strip()
        self.padelpy_version     = self.ed_padelpy_version.text().strip()
        self.rdkit_version       = self.ed_rdkit_version.text().strip()
        self.matplotlib_version  = self.ed_matplotlib_version.text().strip()
        self.seaborn_version     = self.ed_seaborn_version.text().strip()
        self.joblib_version      = self.ed_joblib_version.text().strip()
        self.pandas_version      = self.ed_pandas_version.text().strip()
        self.numpy_version       = self.ed_numpy_version.text().strip()

        self.pytorch_cuda_variant = self.ed_pytorch_variant.text().strip() or "cu121"
        self.pytorch_version      = self.ed_pytorch_version.text().strip() or self._defaults["pytorch_version"]
        self.pytorch_index_url    = self.ed_pytorch_index.text().strip() or self._defaults["pytorch_index_url"]
        self.tensorflow_version   = self.ed_tensorflow_version.text().strip() or "2.15.*"
        self.cuml_version         = self.ed_cuml_version.text().strip()

        steps = sum([
            self.check_venv.isChecked(),
            self.check_java.isChecked(),
            self.check_scikitlearn.isChecked(),
            self.check_pycaret.isChecked(),
            self.check_cuml.isChecked(),
            self.check_chembl.isChecked(),
            self.check_padelpy.isChecked(),
            self.check_rdkit.isChecked(),
            self.check_matplotlib.isChecked(),
            self.check_seaborn.isChecked(),
            self.check_joblib.isChecked(),
            self.check_pandas.isChecked(),
            self.check_numpy.isChecked(),
            self.check_pytorch.isChecked(),
            self.check_tensorflow.isChecked(),
            self.check_libs.isChecked(),
        ])
        if steps == 0:
            QMessageBox.information(
                self,
                i18n.t("req_msg_no_selection_title", self._idioma),
                i18n.t("req_msg_no_selection_body", self._idioma),
            )
            self.btn_install.setEnabled(True)
            return

        self.progress.setMaximum(steps)
        self.log.clear()
        self.thread = threading.Thread(target=self._install_selected, daemon=True)
        self.thread.start()

    def _install_selected(self):
        step = 0
        try:
            # 1) venv
            if self.check_venv.isChecked():
                self.log_signal.emit(i18n.t("req_log_ensuring_venv", self._idioma))
                p = ensure_venv("CODRUG")
                self.log_signal.emit(i18n.t("req_log_using_python", self._idioma, python=p['python']))
                step += 1; self.progress_signal.emit(step)
            else:
                p = ensure_venv("CODRUG")  # sempre garante o venv para instalar nos próximos passos

            pybin = p["python"]

            # 2) Java (JRE, system package via apt)
            if self.check_java.isChecked():
                self.log_signal.emit(i18n.t("req_log_installing", self._idioma, name="Java (JRE)"))
                ok = self.install_java(self.java_version, self.rb_java_default.isChecked())
                step += 1; self.progress_signal.emit(step)
                if not ok: return self._abort("Java (JRE)")

            # 3) installs
            if self.check_chembl.isChecked():
                self.log_signal.emit(i18n.t("req_log_installing", self._idioma, name="chembl_webresource_client"))
                spec = self._version_spec("chembl_webresource_client", self.rb_chembl_latest, self.chembl_version)
                ok = self.install_pkg(pybin, spec); step += 1; self.progress_signal.emit(step)
                if not ok: return self._abort("chembl_webresource_client")

            if self.check_scikitlearn.isChecked():
                self.log_signal.emit(i18n.t("req_log_installing", self._idioma, name="scikit-learn"))
                spec = self._version_spec("scikit-learn", self.rb_scikitlearn_latest, self.scikitlearn_version)
                ok = self.install_pkg(pybin, spec); step += 1; self.progress_signal.emit(step)
                if not ok: return self._abort("scikit-learn")

            if self.check_pycaret.isChecked():
                self.log_signal.emit(i18n.t("req_log_installing", self._idioma, name="PyCaret"))
                spec = self._version_spec("pycaret[full]", self.rb_pycaret_latest, self.pycaret_version)
                ok = self.install_pkg(pybin, spec)
                step += 1; self.progress_signal.emit(step)
                if not ok: return self._abort("PyCaret")

            if self.check_cuml.isChecked():
                self.log_signal.emit(i18n.t("req_log_installing", self._idioma, name="cuML (RAPIDS)"))
                ok = self.install_cuml(pybin)
                step += 1; self.progress_signal.emit(step)
                if not ok: return self._abort("cuML")

            if self.check_padelpy.isChecked():
                self.log_signal.emit(i18n.t("req_log_installing", self._idioma, name="padelpy"))
                spec = self._version_spec("padelpy", self.rb_padelpy_latest, self.padelpy_version)
                ok = self.install_pkg(pybin, spec)
                step += 1; self.progress_signal.emit(step)
                if not ok: return self._abort("padelpy")

            if self.check_rdkit.isChecked():
                self.log_signal.emit(i18n.t("req_log_installing", self._idioma, name="RDKit (rdkit-pypi)"))
                spec = self._version_spec("rdkit-pypi", self.rb_rdkit_latest, self.rdkit_version)
                ok = self.install_pkg(pybin, spec)
                step += 1; self.progress_signal.emit(step)
                if not ok: return self._abort("rdkit-pypi")

            if self.check_matplotlib.isChecked():
                self.log_signal.emit(i18n.t("req_log_installing", self._idioma, name="Matplotlib"))
                spec = self._version_spec("matplotlib", self.rb_matplotlib_latest, self.matplotlib_version)
                ok = self.install_pkg(pybin, spec)
                step += 1; self.progress_signal.emit(step)
                if not ok: return self._abort("matplotlib")

            if self.check_seaborn.isChecked():
                self.log_signal.emit(i18n.t("req_log_installing", self._idioma, name="Seaborn"))
                spec = self._version_spec("seaborn", self.rb_seaborn_latest, self.seaborn_version)
                ok = self.install_pkg(pybin, spec)
                step += 1; self.progress_signal.emit(step)
                if not ok: return self._abort("seaborn")

            if self.check_joblib.isChecked():
                self.log_signal.emit(i18n.t("req_log_installing", self._idioma, name="joblib"))
                spec = self._version_spec("joblib", self.rb_joblib_latest, self.joblib_version)
                ok = self.install_pkg(pybin, spec)
                step += 1; self.progress_signal.emit(step)
                if not ok: return self._abort("joblib")

            if self.check_pandas.isChecked():
                self.log_signal.emit(i18n.t("req_log_installing", self._idioma, name="pandas"))
                spec = self._version_spec("pandas", self.rb_pandas_latest, self.pandas_version)
                ok = self.install_pkg(pybin, spec)
                step += 1; self.progress_signal.emit(step)
                if not ok: return self._abort("pandas")

            if self.check_numpy.isChecked():
                self.log_signal.emit(i18n.t("req_log_installing", self._idioma, name="numpy"))
                spec = self._version_spec("numpy", self.rb_numpy_latest, self.numpy_version)
                ok = self.install_pkg(pybin, spec)
                step += 1; self.progress_signal.emit(step)
                if not ok: return self._abort("numpy")

            if self.check_pytorch.isChecked():
                self.log_signal.emit(i18n.t("req_log_installing", self._idioma, name="PyTorch"))
                ok = self.install_pytorch(pybin)
                step += 1; self.progress_signal.emit(step)
                if not ok: return self._abort("PyTorch")

            if self.check_tensorflow.isChecked():
                self.log_signal.emit(i18n.t("req_log_installing", self._idioma, name="TensorFlow"))
                ok = self.install_tensorflow(pybin)
                step += 1; self.progress_signal.emit(step)
                if not ok: return self._abort("TensorFlow")

            if self.check_libs.isChecked():
                self.log_signal.emit(i18n.t("req_log_installing_default_libs", self._idioma))
                ok = self.install_libs_default(pybin)
                step += 1; self.progress_signal.emit(step)
                if not ok: return self._abort("default libraries")

            self.log_signal.emit(i18n.t("req_log_all_installed", self._idioma))
        finally:
            self.enable_install_signal.emit(True)

    def _abort(self, name: str):
        self.log_signal.emit(i18n.t("req_log_aborted", self._idioma, name=name))

    def _log(self, msg):
        self.log.append(msg)
        scrollbar = self.log.verticalScrollBar()
        if scrollbar is not None:
            scrollbar.setValue(scrollbar.maximum())

    def _set_progress(self, value):
        self.progress.setValue(value)

    def _set_install_enabled(self, enabled):
        self.btn_install.setEnabled(enabled)

    # --------------------------- installers ---------------------------

    def install_java(self, version: str, use_default: bool) -> bool:
        """
        Instala o JRE via apt (pacote de sistema, não pip). 'use_default' instala
        'default-jre'; caso contrário instala 'openjdk-<version>-jre'.
        """
        if not _supports_apt_bootstrap():
            self.log_signal.emit(i18n.t("req_log_java_skip", self._idioma))
            return True
        pkg = "default-jre" if use_default else f"openjdk-{version}-jre"
        if _run_interactive(["sudo", "apt", "update"]) != 0:
            self.log_signal.emit(i18n.t("req_log_java_apt_update_failed", self._idioma))
            return False
        if _run_interactive(["sudo", "apt", "install", "-y", pkg]) != 0:
            self.log_signal.emit(i18n.t("req_log_java_apt_install_failed", self._idioma, pkg=pkg))
            return False
        self.log_signal.emit(i18n.t("req_log_pkg_installed", self._idioma, spec=pkg))
        return True

    def install_pkg(self, pybin: str, spec: str) -> bool:
        res = _pip_install(pybin, [spec])
        if res.returncode != 0:
            self.log_signal.emit(res.stdout + "\n")
            return False
        self.log_signal.emit(i18n.t("req_log_pkg_installed", self._idioma, spec=spec))
        return True

    def build_default_libs_specs(self) -> dict:
        """
        Default extra packages (all via pip).
        """
        return {
            "unzip": None,  # may be skipped if pip can't find; harmless
            "tk": None,     # often provided by OS; pip name may differ
            "fastapi": None,
            "uvicorn": None,
            "python-multipart": None,
            "pydantic": None,
            "xgboost": None,
            "lightgbm": None,
            "scikit-posthocs": None,
            "pygam": None,
            "statsmodels": None,
            "patsy": None,
            "streamlit": None,
            "psutil": None,
            "openpyxl": None,
            "python-docx": None,  # STEP 8 "Generate Final Report" (.docx)
            "Pillow": None,       # composite report figures (module_report)
        }

    def install_libs_default(self, pybin: str) -> bool:
        specs = self.build_default_libs_specs()
        ok_all = True
        for name, ver in specs.items():
            target = f"{name}=={ver}" if ver else name
            res = _pip_install(pybin, [target])
            if res.returncode != 0:
                self.log_signal.emit(i18n.t("req_log_pkg_install_warn", self._idioma, target=target, output=res.stdout))
                ok_all = False
            else:
                self.log_signal.emit(i18n.t("req_log_pkg_installed", self._idioma, spec=target))
        return ok_all

    def install_pytorch(self, pybin: str) -> bool:
        variant = (self.pytorch_cuda_variant or self._defaults["pytorch_variant"]).lower()
        version = "" if self.rb_pytorch_latest.isChecked() else self.pytorch_version.strip()
        base_pkgs = ["torch", "torchvision", "torchaudio"]

        if variant not in ("cu128", "cu121", "cu118", "cpu"):
            self.log_signal.emit(i18n.t("req_log_invalid_pytorch_variant", self._idioma, variant=variant))
            return False

        index_url = self.pytorch_index_url.strip() or self._defaults["pytorch_index_url"]

        specs = [f"{p}=={version}" for p in base_pkgs] if version else base_pkgs
        cmd = [pybin, "-m", "pip", "install", "--upgrade", "--index-url", index_url] + specs
        res = _run(cmd)
        if res.returncode != 0:
            self.log_signal.emit(res.stdout + "\n")
            return False
        self.log_signal.emit(
            i18n.t("req_log_pytorch_installed", self._idioma, variant=variant, version=(' ' + version if version else ""))
        )
        return True

    def install_cuml(self, pybin: str) -> bool:
        if not self.cuml_available:
            self.log_signal.emit(
                i18n.t("req_log_cuml_skip", self._idioma, reason=self._defaults.get('cuml_reason'))
            )
            return True
        pkg = self.cuml_pkg or "cuml-cu12"
        version = "" if self.rb_cuml_latest.isChecked() else self.cuml_version.strip()
        spec = f"{pkg}=={version}" if version else pkg
        cmd = [pybin, "-m", "pip", "install", "--extra-index-url", "https://pypi.nvidia.com", spec]
        res = _run(cmd)
        if res.returncode != 0:
            self.log_signal.emit(res.stdout + "\n")
            return False
        self.log_signal.emit(i18n.t("req_log_cuml_installed", self._idioma, spec=spec))
        return True

    def install_tensorflow(self, pybin: str) -> bool:
        ver = "" if self.rb_tensorflow_latest.isChecked() else (self.tensorflow_version or "").strip()
        spec = f"tensorflow=={ver}" if ver else "tensorflow"
        res = _pip_install(pybin, [spec])
        if res.returncode != 0:
            self.log_signal.emit(res.stdout + "\n")
            return False
        self.log_signal.emit(
            i18n.t("req_log_tensorflow_installed", self._idioma, ver=(ver or i18n.t("req_opt_latest", self._idioma)))
        )
        return True


# For direct test
if __name__ == "__main__":
    if not bootstrap_pyqt5(interactive=True, reexec=True):
        sys.exit(1)
    if not _PYQT_AVAILABLE:
        raise RuntimeError(f"PyQt5 is required to run RequirementsInstaller directly: {_PYQT_IMPORT_ERROR}")
    app = QApplication(sys.argv)
    w = RequirementsInstaller()
    w.show()
    sys.exit(app.exec_())

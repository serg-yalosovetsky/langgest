# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Voice & Gesture Desktop Assistant.

Models (sherpa-onnx, faster-whisper) are NOT bundled here —
they are large and downloaded/placed separately by the user.
Config YAML files and assets ARE bundled as data.
"""

import sys
from pathlib import Path

block_cipher = None

# ---------------------------------------------------------------------------
# Hidden imports: modules discovered at runtime that PyInstaller misses
# ---------------------------------------------------------------------------
hidden_imports = [
    # stdlib used dynamically
    "queue",
    "threading",
    "unicodedata",
    "difflib",
    "fnmatch",
    "webbrowser",
    "subprocess",
    "signal",
    "sqlite3",
    "json",
    "logging",
    "logging.handlers",
    # PyYAML
    "yaml",
    "yaml.loader",
    "yaml.dumper",
    # rapidfuzz (optional fast fuzzy matching)
    "rapidfuzz",
    "rapidfuzz.fuzz",
    "rapidfuzz.process",
    # Windows automation
    "pyautogui",
    "pygetwindow",
    "pyperclip",
    # PySide6 tray
    "PySide6",
    "PySide6.QtWidgets",
    "PySide6.QtGui",
    "PySide6.QtCore",
]

# ---------------------------------------------------------------------------
# Data files bundled into the executable directory
# ---------------------------------------------------------------------------
datas = [
    # Config files (user-editable; copied next to exe so users can find them)
    ("config", "config"),
    ("assets", "assets"),
]

# ---------------------------------------------------------------------------
# Binaries / excludes
# ---------------------------------------------------------------------------
excludes = [
    # Heavy ML libraries not needed at import time (loaded lazily)
    "torch",
    "torchvision",
    "torchaudio",
    "tensorflow",
    "jax",
    # Test / dev tools
    "pytest",
    "mypy",
    "ruff",
    # Jupyter
    "IPython",
    "notebook",
    "ipykernel",
    # Matplotlib (not used)
    "matplotlib",
    "PIL",
]

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
a = Analysis(
    ["src/app/main.py"],
    pathex=["src"],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,           # onedir mode: keeps DLLs next to exe
    name="voice_gesture_assistant",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                        # compress with UPX if available
    console=True,                    # keep console for debug output; set False for tray-only mode
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon="assets/icons/app.ico",   # uncomment after placing icon file
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="voice_gesture_assistant",
)

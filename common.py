# YuiFlix V11 - Shared imports, paths, style and helpers

import os
import sys
import sqlite3
import hashlib
import shutil
from datetime import datetime

from PySide6.QtCore import (
    Qt,
    QTimer,
    Signal,
    QSize,
    QUrl,
)
from PySide6.QtGui import (
    QPixmap,
    QKeySequence,
    QShortcut,
)
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QDialog,
    QMessageBox,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFormLayout,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QScrollArea,
    QStackedWidget,
    QFrame,
    QListWidget,
    QListWidgetItem,
    QFileDialog,
    QProgressBar,
    QSlider,
    QSizePolicy,
    QTextEdit,
    QInputDialog,
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget


# ==============================================================
# PATHS
# ==============================================================

APP_NAME = "YuiFlix"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
POSTER_DIR = os.path.join(ASSETS_DIR, "posters")
VIDEO_DIR = os.path.join(ASSETS_DIR, "videos")

DB_PATH = os.path.join(DATA_DIR, "yuiflix.db")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(POSTER_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)


# ==============================================================
# GLOBALS
# ==============================================================

CURRENT_PROFILE_ID = None
CURRENT_USER_ID = None


# ==============================================================
# STYLE
# ==============================================================

APP_STYLE = """
QMainWindow, QWidget {
    background-color: #141414;
    color: #ffffff;
    font-family: Arial;
}

QLabel {
    color: #ffffff;
}

QPushButton {
    background-color: #242424;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 9px 16px;
}

QPushButton:hover {
    background-color: #333333;
}

QPushButton:pressed {
    background-color: #444444;
}

QLineEdit,
QComboBox,
QSpinBox,
QDoubleSpinBox,
QTextEdit {
    background-color: #222222;
    color: white;
    border: 1px solid #444444;
    border-radius: 5px;
    padding: 8px;
}

QComboBox QAbstractItemView {
    background-color: #222222;
    color: white;
    selection-background-color: #e50914;
}

QScrollArea {
    border: none;
    background: transparent;
}

QSlider::groove:horizontal {
    height: 5px;
    background: #444444;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    width: 13px;
    margin: -4px 0;
    border-radius: 7px;
    background: #e50914;
}

QProgressBar {
    background-color: #333333;
    border: none;
    border-radius: 4px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #e50914;
    border-radius: 4px;
}

QListWidget {
    background-color: #1b1b1b;
    border: 1px solid #333333;
}

QListWidget::item:selected {
    background-color: #e50914;
}

QFrame#card {
    background-color: #1d1d1d;
    border-radius: 6px;
}

QFrame#card:hover {
    background-color: #282828;
}

QFrame#hero {
    background-color: #101010;
    border-radius: 10px;
}

QFrame#adminCard {
    background-color: #202020;
    border-radius: 8px;
}

QFrame#upNext {
    background-color: rgba(20, 20, 20, 235);
    border: 1px solid #555555;
    border-radius: 10px;
}
"""


# ==============================================================
# HELPERS
# ==============================================================

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def format_time(seconds):
    seconds = max(0, int(seconds or 0))

    minutes = seconds // 60
    secs = seconds % 60

    hours = minutes // 60
    minutes %= 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"

    return f"{minutes}:{secs:02d}"


def asset_path(folder, filename):
    if not filename:
        return ""

    path = os.path.join(folder, filename)

    if os.path.exists(path):
        return path

    return ""


def copy_asset(source, folder):
    if not source:
        return ""

    if not os.path.exists(source):
        return ""

    filename = os.path.basename(source)

    destination = os.path.join(folder, filename)

    try:
        shutil.copy2(source, destination)
    except Exception:
        return ""

    return filename


# ==============================================================
# DATABASE
# ==============================================================

# YuiFlix V11 - Application Entry Point

import sys

from PySide6.QtWidgets import QApplication

from common import APP_NAME, APP_STYLE
from main_window import MainWindow
from database import db


def main():
    app = QApplication(sys.argv)

    app.setApplicationName(APP_NAME)
    app.setStyleSheet(APP_STYLE)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

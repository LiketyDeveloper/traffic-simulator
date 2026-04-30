import sys

from PySide6.QtWidgets import QApplication

from src.window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow(app)
    main_window.show()
    app.exec()

from PySide6.QtWidgets import QApplication

from qt_visual_utils.window import MainWindow

def main():
    app = QApplication()
    main_window = MainWindow(app)
    main_window.show()
    app.exec()

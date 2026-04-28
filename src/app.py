import sys
from typing import Sequence

from PySide6.QtWidgets import QApplication

from src.window import MainWindow


class TrafficSimulationApp(QApplication):
    def __init__(self, arguments: Sequence[str]) -> None:
        super().__init__(arguments)

        self.main_window = MainWindow(self)
        self.main_window.show()


if __name__ == "__main__":
    app = TrafficSimulationApp(sys.argv)
    app.exec()

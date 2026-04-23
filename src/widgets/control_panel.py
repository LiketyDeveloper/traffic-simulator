from typing import Callable
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QComboBox, QDockWidget, QVBoxLayout, QWidget

from src.grid import (
    Car,
    GridObject,
    Road,
    Crossroad,
    TrafficLight,
    Pedestrian,
    Crossing,
    Sign,
)

type GridObjectFactory = Callable[[], GridObject]


class ControlPanel(QDockWidget):
    factory_selected = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Управление", parent)

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )

        self.placeable_objects: list[tuple[str, Callable[[], GridObject]]] = [
            ("Автомобиль", Car),
            ("Дорога", Road),
            ("Перекресток", Crossroad),
            ("Светофор", TrafficLight),
            ("Пешеход", Pedestrian),
            ("Пешеходный переход", Crossing),
            ("Знак", Sign),
        ]

        self._build_ui()

    def _build_ui(self) -> None:
        container = QWidget()

        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.combo = QComboBox()
        self.combo.addItem("Выберите объект")

        for name, _ in self.placeable_objects:
            self.combo.addItem(name)

        self.combo.setCurrentIndex(0)
        self.combo.currentIndexChanged.connect(self._on_selection_changed)

        layout.addWidget(self.combo)
        layout.addStretch()

        self.setWidget(container)

    @Slot(int)
    def _on_selection_changed(self, index: int) -> None:
        if index == 0:
            self.factory_selected.emit(None)
        else:
            _, factory = self.placeable_objects[index - 1]
            self.factory_selected.emit(factory)

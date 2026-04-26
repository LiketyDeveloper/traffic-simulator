from asyncio import Transport
from typing import Callable

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QDockWidget,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.grid import (
    Car,
    GridObject,
    Road,
    Crossroad,
    TrafficLight,
    Pedestrian,
    Crossing,
    Sign,
    TLMode,
)

type GridObjectFactory = Callable[[], GridObject]


class ControlPanel(QDockWidget):
    factory_selected = Signal(object)
    tl_mode_changed = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Управление", parent)

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )

        self.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

        self.placeable_objects: list[tuple[str, Callable[[], GridObject]]] = [
            ("Автомобиль", Car),
            # ("Дорога", Road),
            # ("Перекресток", Crossroad),
            ("Светофор", TrafficLight),
            ("Пешеход", Pedestrian),
            ("Пешеходный переход", Crossing),
            ("Знак", Sign),
        ]

        self.tl_modes: list[tuple[str, TLMode]] = [
            ("Режим по времени", TLMode.TIME),
            ("Режим по транспорту", TLMode.TRANSPORT),
        ]

        self.build_ui()

    def restore_object_selection(self):
        self.placement_combo.setCurrentIndex(0)

    def build_ui(self) -> None:
        container = QWidget()
        self.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        placement_section = self.create_placement_section()
        tl_mode_section = self.create_tl_section()
        run_section = self.create_run_section()

        layout.addWidget(placement_section)
        layout.addWidget(tl_mode_section)
        layout.addWidget(run_section)
        layout.addStretch()

    def create_placement_section(self) -> QGroupBox:
        group_box = QGroupBox("Размещение", self)
        layout = QVBoxLayout(group_box)

        self.placement_combo = QComboBox()
        self.placement_combo.addItem("Выберите объект")

        for name, _ in self.placeable_objects:
            self.placement_combo.addItem(name)

        self.placement_combo.setCurrentIndex(0)
        self.placement_combo.currentIndexChanged.connect(self._on_selection_changed)

        layout.addWidget(self.placement_combo)

        return group_box

    def create_tl_section(self) -> QGroupBox:
        group_box = QGroupBox("Режим светофоров")
        layout = QVBoxLayout(group_box)

        self.tl_mode_combo = QComboBox()

        for name, _ in self.tl_modes:
            self.tl_mode_combo.addItem(name)

        self.tl_mode_combo.setCurrentIndex(0)
        self.tl_mode_combo.currentIndexChanged.connect(self._on_tl_mode_changed)

        layout.addWidget(self.tl_mode_combo)

        return group_box

    def create_run_section(self) -> QGroupBox:
        group_box = QGroupBox("Запуск")
        layout = QHBoxLayout(group_box)

        test_template_btn = QPushButton("Тест-шаблон")
        test_random_btn = QPushButton("Тест-рандом")

        layout.addWidget(test_template_btn)
        layout.addWidget(test_random_btn)

        return group_box

    @Slot(int)
    def _on_selection_changed(self, index: int) -> None:
        if index == 0:
            self.factory_selected.emit(None)
        else:
            _, factory = self.placeable_objects[index - 1]
            self.factory_selected.emit(factory)

    @Slot(object)
    def _on_tl_mode_changed(self, index: int) -> None:
        _, tl_mode = self.tl_modes[index]
        self.tl_mode_changed.emit(tl_mode)

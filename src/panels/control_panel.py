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

from src.entities import Crossing, Pedestrian, StraightRoad, CrossRoad, TrafficLight, Sign
from src.types import TLMode, EntityFactory


class ControlPanel(QDockWidget):
    entityFactorySelected = Signal(object)
    tlModeChanged = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Управление", parent)

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )

        self.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

        self.placeableObjects: list[tuple[str, EntityFactory]] = [
            ("Светофор", TrafficLight),
            ("Пешеход", Pedestrian),
            ("Пешеходный переход", Crossing),
            ("Знак", Sign),
            ("Дорога", StraightRoad),
            ("Перекресток", CrossRoad),
        ]

        self.tlModes: list[tuple[str, TLMode]] = [
            ("Режим по времени", TLMode.TIME),
            ("Режим по транспорту", TLMode.TRANSPORT),
        ]

        self.buildUi()

    def deselectEntityFactory(self):
        self.entityCombo.setCurrentIndex(0)

    def buildUi(self) -> None:
        container = QWidget()
        self.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        placementSection = self.create_placement_section()
        tlModeSection = self.create_tl_section()
        runSection = self.create_run_section()

        layout.addWidget(placementSection)
        layout.addWidget(tlModeSection)
        layout.addWidget(runSection)
        layout.addStretch()

    def create_placement_section(self) -> QGroupBox:
        group_box = QGroupBox("Размещение", self)
        layout = QVBoxLayout(group_box)

        self.entityCombo = QComboBox()
        self.entityCombo.addItem("Выберите объект")

        for name, _ in self.placeableObjects:
            self.entityCombo.addItem(name)

        self.entityCombo.setCurrentIndex(0)
        self.entityCombo.currentIndexChanged.connect(self.onSelectionChanged)

        layout.addWidget(self.entityCombo)

        return group_box

    def create_tl_section(self) -> QGroupBox:
        groupBox = QGroupBox("Режим светофоров")
        layout = QVBoxLayout(groupBox)

        self.tlModeCombo = QComboBox()

        for name, _ in self.tlModes:
            self.tlModeCombo.addItem(name)

        self.tlModeCombo.setCurrentIndex(0)
        self.tlModeCombo.currentIndexChanged.connect(self.onTlModeChanged)

        layout.addWidget(self.tlModeCombo)

        return groupBox

    def create_run_section(self) -> QGroupBox:
        groupBox = QGroupBox("Запуск")
        layout = QHBoxLayout(groupBox)

        testTemplateBtn = QPushButton("Тест-шаблон")
        testRandomBtn = QPushButton("Тест-рандом")

        layout.addWidget(testTemplateBtn)
        layout.addWidget(testRandomBtn)

        return groupBox

    @Slot(int)
    def onSelectionChanged(self, index: int) -> None:
        if index == 0:
            self.entityFactorySelected.emit(None)
        else:
            _, factory = self.placeableObjects[index - 1]
            self.entityFactorySelected.emit(factory)

    @Slot(object)
    def onTlModeChanged(self, index: int) -> None:
        _, tlMode = self.tlModes[index]
        self.tlModeChanged.emit(tlMode)

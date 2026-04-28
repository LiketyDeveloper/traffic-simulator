from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QDockWidget,
    QGroupBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.entities import (
    Crossing,
    CrossRoad,
    Pedestrian,
    Sign,
    StraightRoad,
    TrafficLight,
)
from src.types import EntityFactory, TLMode


class ControlPanel(QDockWidget):
    entityFactorySelected = Signal(object)
    tlModeChanged = Signal(object)
    spawnCarsClicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Управление", parent)

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )

        self.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

        self.placeableObjects: list[tuple[str, EntityFactory]] = [
            ("Дорога", StraightRoad),
            ("Перекресток", CrossRoad),
            ("Светофор", TrafficLight),
            ("Пешеход", Pedestrian),
            ("Пешеходный переход", Crossing),
            ("Знак", Sign),
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

        placementSection = self.createPlacementSection()
        tlModeSection = self.createTlSection()
        spawnCarsBtn = self.createSpawnCarsBtn()

        layout.addWidget(placementSection)
        layout.addWidget(tlModeSection)
        layout.addWidget(spawnCarsBtn)

        layout.addStretch()

    def createPlacementSection(self) -> QGroupBox:
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

    def createTlSection(self) -> QGroupBox:
        groupBox = QGroupBox("Режим светофоров")
        layout = QVBoxLayout(groupBox)

        self.tlModeCombo = QComboBox()

        for name, _ in self.tlModes:
            self.tlModeCombo.addItem(name)

        self.tlModeCombo.setCurrentIndex(0)
        self.tlModeCombo.currentIndexChanged.connect(self.onTlModeChanged)

        layout.addWidget(self.tlModeCombo)

        return groupBox

    def createSpawnCarsBtn(self) -> QPushButton:
        spawnCarsBtn = QPushButton("Тест-рандом")

        spawnCarsBtn.clicked.connect(lambda: self.spawnCarsClicked.emit())

        return spawnCarsBtn

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

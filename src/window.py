import random
from PySide6.QtCore import QPoint, QTimer, Qt, Slot
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGraphicsView,
    QLabel,
    QMainWindow,
)

from src.persistence import loadWorld, saveWorld
from src.entities import BaseEntity, Car, TrafficLight
from src.world import World
from src.panels import ControlPanel, PropertiesPanel
from src.types import EntityFactory, SpawnMode, TLMode
from src.utils import scenePosToCell


class MainWindow(QMainWindow):
    def __init__(self, app: QApplication) -> None:
        super().__init__()

        self.app = app

        self.entityFactory: EntityFactory | None = None
        self.spawnMode: SpawnMode | None = None

        self.setupWindow()
        self.setupLayout()

        self.spawnTimer = QTimer()
        self.spawnTimer.setSingleShot(True)
        self.spawnTimer.timeout.connect(self.onSpawnTimerTimeout)

    def setupWindow(self) -> None:
        self.setWindowTitle("Traffic Simulator")
        self.resize(1100, 700)

        menu = self.menuBar().addMenu("Файл")

        save_action = menu.addAction("Сохранить")
        load_action = menu.addAction("Загрузить")

        save_action.triggered.connect(self.save)
        load_action.triggered.connect(self.load)

    def setupLayout(self) -> None:
        self.world = World()
        self.world.onWorldCellClicked.connect(self.onWorldCellClicked)
        self.world.selectionChanged.connect(self.onSelectionChanged)
        self.setCentralWidget(WorldView(self.world))

        self.controlPanel = ControlPanel(self)
        self.controlPanel.entityFactorySelected.connect(self.onFactorySelected)
        self.controlPanel.spawnModeChanged.connect(self.onSpawnModeChanged)
        self.controlPanel.tlModeChanged.connect(self.onTlModeChanged)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.controlPanel)

        self.propertiesPanel = PropertiesPanel()
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.propertiesPanel)

    @Slot(object)
    def onFactorySelected(self, factory: EntityFactory) -> None:
        self.entityFactory = factory

    @Slot(object)
    def onWorldCellClicked(self, cell: QPoint) -> None:
        if self.entityFactory:
            entity = self.entityFactory()

            if entity.validatePlacement(cell, self.world):
                entity.setCell(cell)
                self.world.addItem(entity)

            self.controlPanel.deselectEntityFactory()

    @Slot()
    def onSelectionChanged(self) -> None:
        entities = self.world.selectedItems()
        entity = entities[0] if entities else None

        if not isinstance(entity, BaseEntity):
            entity = None

        self.propertiesPanel.selectedEntity = entity

    @Slot(object)
    def onTlModeChanged(self, tlMode: TLMode) -> None:
        for tl in self.world.entities(TrafficLight):
            tl.mode = tlMode

    @Slot(object)
    def onSpawnModeChanged(self, spawnMode: SpawnMode) -> None:
        for car in self.world.entities(Car):
            car.scene().removeItem(car)
        if spawnMode == self.spawnMode:
            self.spawnMode = None
        else:
            self.spawnMode = spawnMode
        self.onSpawnTimerTimeout()

    @Slot()
    def onSpawnTimerTimeout(self) -> None:
        if self.spawnMode == SpawnMode.RANDOM:
            self.spawnRandomCar()
            intervalMs = random.randint(1000, 3000)
            self.spawnTimer.start(intervalMs)

        elif self.spawnMode == SpawnMode.TEMPLATE:
            self.spawnTemplateCars()
            self.spawnTimer.start(7000)

    def spawnRandomCar(self) -> None:
        path = self.world.generateRandomPath()
        if path:
            car = Car(path)
            self.world.addItem(car)

    def spawnTemplateCars(self) -> None:
        for path in self.world.templatePaths:
            car = Car(path)
            self.world.addItem(car)

    def save(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить", "", "JSON (*.json)")

        if path:
            if not path.endswith(".json"):
                path += ".json"
            saveWorld(self.world, path)

    def load(self):
        path, _ = QFileDialog.getOpenFileName(self, "", "Загрузить", "JSON (*.json)")
        if path:
            loadWorld(self.world, path)


class WorldView(QGraphicsView):
    def __init__(self, world: World, parent=None):
        super().__init__(world, parent)

        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing, False)

        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.cursorLabel = QLabel(self.viewport())
        self.cursorLabel.setFrameStyle(QLabel.Shape.StyledPanel)
        self.cursorLabel.setAutoFillBackground(True)
        self.cursorLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.cursorLabel.hide()

    def mouseMoveEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        cell = scenePosToCell(scene_pos)

        self.cursorLabel.setText(f"{cell.x()}, {cell.y()}")
        self.cursorLabel.adjustSize()

        self.cursorLabel.move(event.pos() + QPoint(12, 12))

        super().mouseMoveEvent(event)

    def enterEvent(self, event):
        self.cursorLabel.show()
        super().leaveEvent(event)

    def leaveEvent(self, event):
        self.cursorLabel.hide()
        super().leaveEvent(event)

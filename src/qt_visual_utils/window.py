import random

from PySide6.QtCore import QPoint, Qt, QTimer, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QGraphicsView,
    QLabel,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from qt_visual_utils.arduino import arduino
from qt_visual_utils.database import eventDb
from qt_visual_utils.entities import BaseEntity, Car, TrafficLight
from qt_visual_utils.panels import ControlPanel, PropertiesPanel
from qt_visual_utils.persistence import loadWorld, saveWorld
from qt_visual_utils.types import EntityFactory, TLMode
from qt_visual_utils.utils import getPrettyTimestamp, scenePosToCell
from qt_visual_utils.world import World


class MainWindow(QMainWindow):
    def __init__(self, app: QApplication) -> None:
        super().__init__()

        self.app = app

        self.entityFactory: EntityFactory | None = None

        self.setupWindow()
        self.setupLayout()

        self.shouldSpawnCar = False
        self.events_window = None

        self.spawnTimer = QTimer()
        self.spawnTimer.setSingleShot(True)
        self.spawnTimer.timeout.connect(self.onSpawnTimerTimeout)

        self.trackedTl = None

        eventDb.log(f"Application startup, arduino: {arduino.port or 'Not Connected'}")

    def setupWindow(self) -> None:
        self.setWindowTitle("ИИС Дорожной системы")
        self.resize(1100, 700)

        menu = self.menuBar().addMenu("Файл")

        self.setWindowIcon(QIcon(getMediaPath("TLgreen.ico")))

        save_action = menu.addAction("Сохранить")
        load_action = menu.addAction("Загрузить")

        events_action = self.menuBar().addAction("События")
        events_action.triggered.connect(self.openEventsWindow)

        save_action.triggered.connect(self.save)
        load_action.triggered.connect(self.load)

    def setupLayout(self) -> None:
        self.world = World()
        self.world.onWorldCellClicked.connect(self.onWorldCellClicked)
        self.world.selectionChanged.connect(self.onSelectionChanged)
        self.setCentralWidget(WorldView(self.world))

        self.controlPanel = ControlPanel(self)
        self.controlPanel.entityFactorySelected.connect(self.onFactorySelected)
        self.controlPanel.spawnCarsClicked.connect(self.onSpawnCarsClicked)
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
                eventDb.log(
                    f"Place {type(entity).__name__} at ({cell.x()}, {cell.y()})"
                )

            self.controlPanel.deselectEntityFactory()

    @Slot()
    def onSelectionChanged(self) -> None:
        entities = self.world.selectedItems()
        entity = entities[0] if entities else None

        if not isinstance(entity, BaseEntity):
            arduino.send("")
            entity = None

        if isinstance(entity, TrafficLight):
            if self.trackedTl is not None:
                self.trackedTl.isTracked = False

            self.trackedTl = entity
            self.trackedTl.isTracked = True

        self.propertiesPanel.selectedEntity = entity

    @Slot(object)
    def onTlModeChanged(self, tlMode: TLMode) -> None:
        eventDb.log(f"Set Traffic Light mode to {tlMode.name}")
        for tl in self.world.entities(TrafficLight):
            tl.mode = tlMode

    @Slot(object)
    def onSpawnCarsClicked(self) -> None:
        for car in self.world.entities(Car):
            car.scene().removeItem(car)

        self.shouldSpawnCar = not self.shouldSpawnCar
        eventDb.log(f"Turn {'on' if self.shouldSpawnCar else 'off'} car spawning")
        self.onSpawnTimerTimeout()

    @Slot()
    def onSpawnTimerTimeout(self) -> None:
        if self.shouldSpawnCar:
            self.spawnRandomCar()
            intervalMs = random.randint(1000, 3000)
            self.spawnTimer.start(intervalMs)

    @Slot()
    def openEventsWindow(self) -> None:
        if self.events_window is None:
            self.events_window = EventsWindow(self)

        self.events_window.load_data()
        self.events_window.show()
        self.events_window.raise_()
        self.events_window.activateWindow()

    def spawnRandomCar(self) -> None:
        entrances = self.world.getEntrances()
        if not entrances:
            return
        path = self.world.generateRandomPath(random.choice(entrances))
        if path:
            car = Car(path)
            self.world.addItem(car)
    
    def closeEvent(self, event) -> None:
        arduino.send("")

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

        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
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


class EventsWindow(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("События")
        self.resize(700, 400)

        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setCascadingSectionResizes(True)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Message"])

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_data)
        layout.addWidget(refresh_btn)

        self.load_data()

    def load_data(self) -> None:
        data = eventDb.fetch_all()

        self.table.setRowCount(len(data))

        for row, (_, ts, msg) in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(getPrettyTimestamp(ts)))
            self.table.setItem(row, 1, QTableWidgetItem(msg))

        self.table.resizeColumnsToContents()

from PySide6.QtCore import QPoint, Qt, Slot
from PySide6.QtWidgets import QApplication, QGraphicsView, QMainWindow

from src.entities import BaseEntity
from src.world import World
from src.panels import ControlPanel, PropertiesPanel
from src.types import EntityFactory


class MainWindow(QMainWindow):
    def __init__(self, app: QApplication) -> None:
        super().__init__()

        self.app = app

        self.entityFactory: EntityFactory | None = None

        self.setupWindow()
        self.setupLayout()

    def setupWindow(self) -> None:
        self.setWindowTitle("Traffic Simulator")
        self.resize(1100, 700)

        menu = self.menuBar().addMenu("Файл")

        save_action = menu.addAction("Сохранить")
        load_action = menu.addAction("Загрузить")

    def setupLayout(self) -> None:
        self.world = World()
        self.world.onWorldCellClicked.connect(self.onWorldCellClicked)
        self.world.selectionChanged.connect(self.onSelectionChanged)
        self.setCentralWidget(QGraphicsView(self.world))

        self.controlPanel = ControlPanel(self)
        self.controlPanel.entityFactorySelected.connect(self.onFactorySelected)
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

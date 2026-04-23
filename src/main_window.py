from PySide6.QtCore import QPoint, Slot
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QApplication, QMainWindow


from .grid import GridView, GridScene, GridObject
from .widgets import ControlPanel, GridObjectFactory, PropertiesPanel


class MainWindow(QMainWindow):
    def __init__(self, app: QApplication) -> None:
        super().__init__()

        self.app = app

        self.object_factory = None

        self.setup_window()
        self.setup_layout()

    def setup_window(self) -> None:
        self.setWindowTitle("Traffic Simulator")
        self.resize(1100, 700)

    def setup_layout(self) -> None:
        self.grid_scene = GridScene()
        self.grid_view = GridView(self.grid_scene)

        self.grid_view.on_click.connect(self.on_grid_view_click)

        self.control_panel = ControlPanel()
        self.control_panel.factory_selected.connect(self.on_factory_selected)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.control_panel)

        self.properties_panel = PropertiesPanel(self.grid_scene, self)
        self.grid_scene.selectionChanged.connect(self.on_selection_change)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_panel)

        self.setCentralWidget(self.grid_view)

    @Slot(object)
    def on_factory_selected(self, factory: GridObjectFactory) -> None:
        self.object_factory = factory

    @Slot(object)
    def on_grid_view_click(self, grid_pos: QPoint) -> None:
        if self.object_factory:
            self.grid_scene.add_item(self.object_factory(), grid_pos)
            self.control_panel.restore_object_selection()

    @Slot()
    def on_selection_change(self) -> None:
        objs = self.grid_scene.selectedItems()
        obj = objs[0] if objs else None

        if not isinstance(obj, GridObject):
            obj = None

        self.properties_panel.set_object(obj)

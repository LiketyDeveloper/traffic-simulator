from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLineEdit,
)

from src.grid import (
    GridScene,
    GridObject,
    Car,
    Road,
    TrafficLight,
    Crossing,
    Sign,
    Direction,
    TrafficLightState,
    Orientation,
    SignType,
)


def enum_editor(enum_type):
    def factory(getter, setter):
        combo = QComboBox()
        combo.addItems([e.name for e in enum_type])
        combo.setCurrentText(getter().name)
        combo.currentTextChanged.connect(lambda v: setter(enum_type[v]))
        return combo

    return factory


class PropertiesPanel(QDockWidget):
    def __init__(self, scene: GridScene, parent=None):
        super().__init__("Свойства", parent)
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )

        self._selected_object = None
        self.build_ui()

    def set_object(self, obj: GridObject | None):
        self._selected_object = obj
        self.update_props()

    def build_ui(self):
        container = QWidget()
        self.setWidget(container)

        layout = QVBoxLayout(container)
        self.props_layout = QVBoxLayout()

        layout.addLayout(self.props_layout)
        layout.addStretch()

        self.update_props()

    def clear(self):
        while self.props_layout.count():
            item = self.props_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def add_row(self, name, widget):
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.addWidget(QLabel(name))
        layout.addWidget(widget)
        self.props_layout.addWidget(row)

    def update_props(self):
        self.clear()

        if not self._selected_object:
            self.props_layout.addWidget(QLabel("Выберите объект..."))
            return

        self.props_layout.addWidget(
            QLabel(f"Тип: {self._selected_object.__class__.__name__}")
        )

        specs = []

        if isinstance(self._selected_object, Car):
            specs = [
                (
                    "Направление",
                    "direction",
                    enum_editor(Direction),
                ),
            ]
        elif isinstance(self._selected_object, Road):
            specs = [
                (
                    "Направление",
                    "direction",
                    enum_editor(Direction),
                ),
            ]
        elif isinstance(self._selected_object, TrafficLight):
            specs = [
                (
                    "Состояние",
                    "state",
                    enum_editor(TrafficLightState),
                ),
            ]

        elif isinstance(self._selected_object, Crossing):
            specs = [
                (
                    "Ориентация",
                    "orientation",
                    enum_editor(Orientation),
                ),
            ]

        elif isinstance(self._selected_object, Sign):
            specs = [
                (
                    "Тип",
                    "sign_type",
                    enum_editor(SignType),
                ),
            ]

        for name, attr, editor_factory in specs:
            getter = self.make_getter(attr)
            setter = self.make_setter(attr)

            widget = editor_factory(getter, setter)
            self.add_row(name, widget)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_object)
        self.props_layout.addWidget(delete_btn)

        self.props_layout.addStretch()

    def make_getter(self, attr):
        def getter():
            return getattr(self._selected_object, attr)

        return getter

    def make_setter(self, attr):
        def setter(value):
            setattr(self._selected_object, attr, value)
            self._selected_object.refresh()

        return setter

    def delete_object(self):
        if self._selected_object:
            self._selected_object.scene().removeItem(self._selected_object)
        self.update_props()

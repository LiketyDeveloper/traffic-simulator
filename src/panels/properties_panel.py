from dataclasses import dataclass
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDockWidget,
    QFormLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.database import eventDb
from src.entities import BaseEntity, Sign, TrafficLight
from src.types import SignType, TLState


def enum_editor(enum_type):
    def factory(getter, setter):
        combo = QComboBox()
        combo.addItems([e.name for e in enum_type])

        combo.setCurrentText(getter().name)

        combo.currentTextChanged.connect(lambda v: setter(enum_type[v]))

        return combo

    return factory


type Getter[T] = Callable[[], T]
type Setter[T] = Callable[[T], None]


@dataclass
class Property[T]:
    name: str
    getter: Getter[T]
    setter: Setter[T]
    editor: Callable[[Getter[T], Setter[T]], QWidget]


class PropertiesPanel(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Свойства", parent)

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

        self.buildUi()

        self.selectedEntity = None

    @property
    def selectedEntity(self) -> BaseEntity | None:
        return self._selectedEntity

    @selectedEntity.setter
    def selectedEntity(self, entity: BaseEntity | None) -> None:
        self._selectedEntity = entity
        self.updateProps()

    def buildUi(self) -> None:
        container = QWidget()
        self.setWidget(container)

        layout = QVBoxLayout(container)
        self.form = QFormLayout()

        layout.addLayout(self.form)

        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_object)

        layout.addWidget(self.delete_btn)
        layout.addStretch()

    def clear_form(self):
        while self.form.rowCount():
            self.form.removeRow(0)

    def updateProps(self):
        self.clear_form()

        if not self.selectedEntity:
            self.form.addRow(QLabel("Выберите объект..."))
            self.delete_btn.hide()
            return

        self.form.addRow(QLabel(f"Тип: {self.selectedEntity.__class__.__name__}"))

        specs = self.get_specs(self.selectedEntity)

        for spec in specs:
            widget = spec.editor(spec.getter, spec.setter)
            self.form.addRow(spec.name, widget)

        self.delete_btn.show()

    def get_specs(self, entity) -> list[Property]:
        if isinstance(entity, TrafficLight):
            return [
                Property(
                    "Cостояние",
                    lambda: getattr(self.selectedEntity, "state"),
                    lambda v: setattr(self.selectedEntity, "state", v),
                    editor=enum_editor(TLState),
                )
            ]

        if isinstance(entity, Sign):
            return [
                Property(
                    "Тип",
                    lambda: getattr(self.selectedEntity, "type"),
                    lambda v: setattr(self.selectedEntity, "type", v),
                    editor=enum_editor(SignType),
                )
            ]

        return []

    def delete_object(self):
        if self.selectedEntity:
            cell = self.selectedEntity.cell
            eventDb.log(f"Remove {type(self.selectedEntity).__name__} at ({cell.x()}, {cell.y()})")
            self.selectedEntity.scene().removeItem(self.selectedEntity)
            self.selectedEntity = None

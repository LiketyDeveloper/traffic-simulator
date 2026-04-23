from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QGraphicsView
from PySide6.QtGui import QPainter

from .scene import GridScene


class GridView(QGraphicsView):
    on_click = Signal(object)

    def __init__(self, scene: GridScene, parent=None):
        super().__init__(scene, parent)

        # Rendering quality
        self.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing, False)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def scene(self) -> GridScene:
        print(super().scene())
        return super().scene()  # type: ignore

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.pos())

            self.on_click.emit(self.scene().pos_to_cell(scene_pos))

        super().mousePressEvent(event)

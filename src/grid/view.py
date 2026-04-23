from PySide6.QtCore import QPoint, Signal, Qt
from PySide6.QtWidgets import QGraphicsView, QLabel
from PySide6.QtGui import QPainter

from .scene import GridScene


class GridView(QGraphicsView):
    on_click = Signal(object)

    def __init__(self, scene: GridScene, parent=None):
        super().__init__(scene, parent)

        # Rendering quality
        self.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing, False)

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.cursor_label = QLabel(self.viewport())
        self.cursor_label.setFrameStyle(QLabel.Shape.StyledPanel)
        self.cursor_label.setAutoFillBackground(True)
        self.cursor_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.cursor_label.hide()

    def scene(self) -> GridScene:
        return super().scene()  # type: ignore

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.pos())

            self.on_click.emit(self.scene().pos_to_cell(scene_pos))

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        cell = self.scene().pos_to_cell(scene_pos)

        self.cursor_label.setText(f"{cell.x()}, {cell.y()}")
        self.cursor_label.adjustSize()

        self.cursor_label.move(event.pos() + QPoint(12, 12))

        super().mouseMoveEvent(event)

    def enterEvent(self, event):
        self.cursor_label.show()
        super().leaveEvent(event)

    def leaveEvent(self, event):
        self.cursor_label.hide()
        super().leaveEvent(event)

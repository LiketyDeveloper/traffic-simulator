== Базовый класс сущности -- BaseEntity <header:BaseEntity>

BaseEntity наследуется от QGraphicsPixmapItem и служит фундаментом для всех
объектов на сцене (дорог, машин, светофоров и т.д.). Он инкапсулирует клеточную
позицию, автоматическое масштабирование текстур, обработку перемещения и
валидацию размещения.

=== Инициализация

Конструктор (@code:BaseEntityInit) принимает два параметра: `zIndex` (порядок
отрисовки) и movable (возможность перемещать объект мышью). По умолчанию все
сущности являются выделяемыми, а если `movable` равен `True`, им также
добавляется флаг перемещения. Начальная клетка определяется преобразованием
текущей позиции в координаты сетки с помощью `scenePosToCell`.

#figure(caption: [Конструктор `BaseEntity`])[
    ```Python
    class BaseEntity(QGraphicsPixmapItem):
        def __init__(
            self, zIndex: int = 0, movable: bool = True
        ) -> None:
            super().__init__()

            flags = QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            if movable:
                flags |= QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            self.setFlags(flags)

            self.setZValue(zIndex)
            self.cell = scenePosToCell(self.pos())
    ```
] <code:BaseEntityInit>

=== Поведение по таймеру

Метод `tick` (@code:tick) вызывается каждым таймером сцены (передаётся время в
секундах, прошедшее с предыдущего вызова). В базовом классе он ничего не делает
и предназначен для переопределения в дочерних классах, где реализуется
специфическое поведение — движение машин, переключение светофоров и т.д.

#figure(caption: [Метод `tick`])[
    ```Python
    def tick(self, dt: float) -> None:
        pass
    ```
] <code:tick>

=== Установка текстуры с автоматическим масштабированием

Метод `setPixmap` (@code:setPixmap) переопределяет поведение базового класса и
автоматически масштабирует переданное изображение до размера клетки
(`CELL_SIZE`). Масштабирование выполняется с сохранением пропорций
(`KeepAspectRatio`) и использованием сглаживания (`SmoothTransformation`) для
качественного отображения.

#figure(caption: [Метод `setPixmap` с автоматическим масштабированием])[
    ```Python
    def mouseReleaseEvent(
        self, event: QGraphicsSceneMouseEvent
    ) -> None:
        super().mouseReleaseEvent(event)
        cell = snapScenePosToCell(self.pos())

        if cell == self.cell or not self.validatePlacement(cell, self.world):
            self.setCell(self.cell)
            return

        self.setCell(cell)
    ```
] <code:setPixmap>

=== Обработка перемещения

При отпускании кнопки мыши после перетаскивания сущности на mouseReleaseEvent
(@code:mouseReleaseEvent) координаты курсора преобразуются в клетку с помощью
`snapScenePosToCell`. Если новая клетка совпадает со старой или размещение в ней
невалидно, сущность возвращается на прежнюю позицию. В противном случае
выполняется перемещение.

#figure(caption: [Метод-событие `mouseReleaseEvent`])[
    ```Python
    def mouseReleaseEvent(
        self, event: QGraphicsSceneMouseEvent
    ) -> None:
        super().mouseReleaseEvent(event)
        cell = snapScenePosToCell(self.pos())

        if cell == self.cell or not self.validatePlacement(cell, self.world):
            self.setCell(self.cell)
            return

        self.setCell(cell)
    ```
] <code:mouseReleaseEvent>

=== Установка позиции

Метод `setCell` (@code:setCell) обновляет внутреннее представление клетки
(`self.cell`) и устанавливает графическую позицию сущности на сцене, преобразуя
координаты клетки в пиксельные через `cellToScenePos`.

#figure(caption: [метод `setCell`])[
    ```Python
    def setCell(self, cell: QPoint) -> None:
        self.cell = cell
        self.setPos(cellToScenePos(cell))
    ```
] <code:setCell>

=== Валидация размещения

Метод `validatePlacement` (@code:validatePlacement) проверяет, можно ли
разместить сущность в заданной клетке. По умолчанию запрещается размещение двух
сущностей одного типа в одной клетке. Дочерние классы могут переопределять этот
метод для более сложных правил.

#figure(caption: [Метод `validatePlacement`])[
    ```Python
    def validatePlacement(self, cell: QPoint, world: "World") -> bool:
        existingItems = world.get(cell, types=type(self))
        return len(existingItems) == 0
    ```
] <code:validatePlacement>

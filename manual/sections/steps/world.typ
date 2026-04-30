== Реализация сцены — класс World

`World` наследуется от `QGraphicsScene` и выступает контейнером, хранящим все
сущности сцены, а также предоставляет методы для их поиска, навигации и
генерации маршрутов. При инициализации задаются цвет фона и сетки,
устанавливается прямоугольник сцены с центром в нулевых координатах, а также
создаётся и запускается таймер симуляции, который с интервалом `tickMs`
управляет поведением всех сущностей.

=== Поиск и навигация по сцене

`World` предоставляет три основных метода для получения сущностей
(@code:entitiesMethods). `entities` возвращает все объекты указанного типа (или
типов). `get` возвращает сущности в конкретной клетке. `getNeighbors` —
сущности, находящиеся в соседних клетках согласно предопределённым направлениям
(`DIR2OFFSET`)

#figure(caption: [Методы получения сущностей])[
    ```Python
    def entities[T: BaseEntity](
        self, types: type[T] | tuple[type[T]]
    ) -> list[T]:
        return [e for e in self.items() if isinstance(e, types)]

    def get[T: BaseEntity](
        self, at: QPoint, types: type[T] | tuple[type[T]] = BaseEntity
    ) -> list[T]:
        return [e for e in self.entities(types) if e.cell == at]

    def getNeighbors[T: BaseEntity](
        self, at: QPoint, types: type[T] | tuple[type[T]] = BaseEntity
    ) -> list[T]:
        neighbors = []
        for _, offset in DIR2OFFSET.items():
            neighbors.extend(self.get(at + offset, types))
        return neighbors
    ```
] <code:entitiesMethods>


=== Обработка нажатия по сцене

При клике на сцене `mousePressEvent` (@code:mousePressEvent) преобразует
координаты события в клетку с помощью `scenePosToCell` и испускает сигнал
`onWorldCellClicked`, который обрабатывается в `MainWindow`.

#figure(
    caption: [Метод `mousePressEvent`],
)[
    ```Python
    def mousePressEvent(
        self, event: QGraphicsSceneMouseEvent
    ) -> None:
        cell = scenePosToCell(event.scenePos())
        self.onWorldCellClicked.emit(cell)
        return super().mousePressEvent(event)
    ```
] <code:mousePressEvent>

=== Отрисовка сетки

`drawBackground` (@code:drawBackground) рисует сетку: сначала заливает фон,
затем линиями размечает клетки с шагом `CELL_SIZE` в пределах видимой области.

#figure(caption: [Метод `drawBackground`])[
    ```Python
    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        painter.fillRect(rect, self.backgroundColor)
        painter.setPen(QPen(self.gridColor, 0.4))

        left, right = int(rect.left()), int(rect.right())
        top, bottom = int(rect.top()), int(rect.bottom())
        first_left = left - (left % CELL_SIZE)
        first_top = top - (top % CELL_SIZE)

        for x in range(first_left, right, CELL_SIZE):
            painter.drawLine(x, top, x, bottom)
        for y in range(first_top, bottom, CELL_SIZE):
            painter.drawLine(left, y, right, y)
    ```
] <code:drawBackground>

=== Обновление сущностей по таймеру

Каждый тик таймера вызывает `onTick` (@code:onTick), который проходит по всем
сущностям сцены и для каждой вызывает метод `tick`, передавая ему прошедшее
время в секундах.

#figure(caption: [Метод `onTick`])[
    ```Python
    def onTick(self) -> None:
        for entity in self.entities():
            entity.tick(self.simTimer.interval() / 1000)
    ```
] <code:onTick>

=== Генерация случайного маршрута

Метод `generateRandomPath` строит маршрут от заданной стартовой дороги длиной не
более `maxLength` клеток. Алгоритм последовательно движется вперёд, обрабатывая
два типа дорог: прямые участки и перекрёстки.

Маршрут начинается со стартовой дороги. Переменная current хранит текущую
позицию на траектории (@code:pathGenInit)

#figure(caption: [Инициализация генерации маршрута])[
    ```Python
    def generateRandomPath(
      self, start: StraightRoad, maxLength: int = 60
    ) -> list[Road]:
        path: list[Road] = [start]
        current = start
    ```
] <code:pathGenInit>


На каждой итерации алгоритм запрашивает у сцены дорогу впереди
(`getCellOffset(1)` возвращает смещение на одну клетку вперёд относительно
направления текущей дороги). Если впереди нет дороги, маршрут прерывается
(@code:pathGenLoop)

#figure(caption: [Основной цикл геренации маршрута])[
    ```Python
    for _ in range(maxLength):
        ahead = self.get(current.getCellOffset(1), Road)
        if not ahead:
            break
        ahead = ahead[0]
    ```
] <code:pathGenLoop>

Если впереди прямая дорога, проверяется совпадение направлений: поворот на
прямой дороге невозможен. При успешной проверке дорога добавляется в маршрут, и
движение продолжается. (@code:pathGenStraight)

#figure(caption: [Обработка прямой дороги])[
    ```Python
    if isinstance(ahead, StraightRoad):
        if current.direction != ahead.direction:
            break
        path.append(ahead)
        current = ahead
        continue
    ```
] <code:pathGenStraight>


При достижении перекрёстка алгоритм получает все возможные варианты проезда
через функцию `expandCrossroadPaths`, которая возвращает последовательности
смещений для каждого типа поворота (прямо, налево, направо, разворот). Варианты
перемешиваются случайным образом. Для каждого варианта проверяется, существует
ли на выходе прямая дорога и можно ли её проехать (`canBePassed`)
(@code:pathGenCrossroad)

#figure(caption: [Обработка перекрестка])[
    ```Python
    if isinstance(ahead, CrossRoad):
        expandedPaths = list(
            expandCrossroadPaths(current.direction).items()
        )
        random.shuffle(expandedPaths)

        for turnType, pathSteps in expandedPaths:
            dst = self.get(current.cell + pathSteps[-1], StraightRoad)
            if not dst or not dst[0].canBePassed():
                continue

            for stepOffset in pathSteps:
                road = self.get(current.cell + stepOffset, Road)
                if not road:
                    break  # if gap in path then abort turn
                path.append(road[0])

            current = dst[0]
            break
    ```
] <code:pathGenCrossroad>

Если выходная дорога доступна, алгоритм последовательно добавляет в маршрут все
клетки перекрёстка согласно предвычисленным смещениям. Текущей позицией
становится выездная дорога, после чего цикл завершается (перекрёсток пройден).
Метод возвращает построенный маршрут.


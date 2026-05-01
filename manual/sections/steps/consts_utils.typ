== Константы и утилиты

Перед реализацией сцены необходимо определить базовые константы и
вспомогательные функции, которые используются всеми компонентами приложения.

=== Константы
`SRC_PATH`, `BASE_PATH` и `MEDIA_PATH` (@code:pathConsts) определяют структуру
каталогов проекта с помощью объектно ориентированной, мультиплатформенной
библиотеки работы с путями для работы на любой машине.

#figure(caption: [Пути к файлам])[
    ```Python
    SRC_PATH = Path(__file__).parent
    BASE_PATH = SRC_PATH.parent
    MEDIA_PATH = BASE_PATH / "media"
    ```
] <code:pathConsts>

`CELL_SIZE` задаёт размер клетки в пикселях (35×35), а `GRID_DIM` определяет
размер сетки 50×50 клеток (@code:cellConsts)

#figure(caption: [Параметры сетки])[
    ```Python
    CELL_SIZE = 35
    GRID_DIM = 50
    ```
] <code:cellConsts>

Словарь `DIR2ROT` сопоставляет направления с углами поворота текстур (в
градусах). `DIR2OFFSET` определяет смещения по координатной сетке: движение на
север уменьшает `Y`, на юг — увеличивает, на запад уменьшает `X`, на восток —
увеличивает. Список `CLOCKWISE` задаёт порядок направлений по часовой стрелке,
что удобно для расчётов поворотов (@code:dirConsts)

#figure(caption: [Направления и смещения])[
    ```Python
    DIR2ROT: dict[Direction, int] = {
        Direction.N: 0,
        Direction.S: 180,
        Direction.W: -90,
        Direction.E: 90,
    }

    DIR2OFFSET: dict[Direction, QPoint] = {
        Direction.N: QPoint(0, -1),
        Direction.S: QPoint(0, 1),
        Direction.W: QPoint(-1, 0),
        Direction.E: QPoint(1, 0),
    }

    CLOCKWISE = [Direction.N, Direction.E, Direction.S, Direction.W]
    ```
] <code:dirConsts>

=== Утилиты

`getMediaPath` возвращает абсолютный путь к медиафайлу (изображению) по его
имени. `getPrettyTimestamp` преобразует временную метку в человекочитаемый
формат для логирования событий (@code:helpers)

#figure(caption: [Вспомогательные функции])[
    ```Python
    def getMediaPath(media_name: str) -> str:
        return str(MEDIA_PATH / media_name)

    def getPrettyTimestamp(timestamp: float) -> str:
        return datetime.fromtimestamp(timestamp).strftime(
           "%Y-%m-%d %H:%M:%S"
        )
    ```
] <code:helpers>


Функции преобразования координат: `scenePosToCell` переводит координаты сцены в
клетку с округлением вниз (используется для определения клетки под курсором
мыши), `snapScenePosToCell` — с математическим округлением, `cellToScenePos`
выполняет обратное преобразование из клетки в пиксельные координаты сцены
(@code:coordUtils)

#figure(caption: [Функции для преобразование координат])[
    ```Python
    def scenePosToCell(pos: QPoint | QPointF) -> QPoint:
        return QPoint(
            math.floor(pos.x() / CELL_SIZE),
            math.floor(pos.y() / CELL_SIZE),
        )

    def snapScenePosToCell(pos: QPoint | QPointF) -> QPoint:
        return QPoint(
            round(pos.x() / CELL_SIZE),
            round(pos.y() / CELL_SIZE),
        )

    def cellToScenePos(cell: QPoint) -> QPoint:
        return QPoint(
            cell.x() * CELL_SIZE,
            cell.y() * CELL_SIZE,
        )
    ```
] <code:coordUtils>


`getDirectionFromOffset` возвращает направление по вектору смещения.
`rotateDirection` вычисляет новое направление после выполнения манёвра (поворот
налево, направо, разворот или движение прямо), используя порядок `CLOCKWISE` и
словарь дельт (@code:dirUtils)

#figure(caption: [Функции для работы с направлением])[
    ```Python
    def getDirectionFromOffset(offset: QPoint) -> Direction:
        for direction, dir_offset in DIR2OFFSET.items():
            if offset == dir_offset:
                return direction
        return Direction.N

    def rotateDirection(
        direction: Direction, turn: TurnType
    ) -> Direction:
        delta = {
            TurnType.FORWARD: 0,
            TurnType.RIGHT: 1,
            TurnType.UTURN: 2,
            TurnType.LEFT: -1,
        }
        return CLOCKWISE[
            (CLOCKWISE.index(direction) + delta[turn]) % 4
        ]
    ```
] <code:dirUtils>

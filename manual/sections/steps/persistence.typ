== Сериализация и загрузка сцены -- модуль persistence

Модуль `persistence` отвечает за сохранение состояния сцены в JSON-файл и
восстановление из него. Это позволяет пользователю сохранять созданные сцены
дорожной сети и загружать их при следующем запуске.

=== Сериализаторы сущностей

`Serializer` (@code:serializer) — это дженерик-датакласс, который связывает пару
функций для конкретного типа сущности: `serialize` преобразует объект в словарь,
а `deserialize` восстанавливает объект из словаря.

#figure(caption: [Dataclass сериализатора сущностей])[
    ```Python
    @dataclass
    class Serializer[T: BaseEntity]:
        serialize: Callable[[T], dict]
        deserialize: Callable[[dict[str, Any]], T]
    ```
] <code:serializer>

=== Регистр сериализаторов

Словарь SERIALIZERS (@code:serializerRegistry) сопоставляет каждый класс
сущности с его сериализатором. Для дорог сохраняется направление, для знаков —
тип, для пешеходных переходов — ориентация. Перекрёстки, светофоры и пешеходы не
имеют дополнительных параметров, поэтому их сериализаторы работают с пустыми
словарями.

#figure(caption: [Регистр сериализаторов])[
    ```Python
    SERIALIZERS: dict[type[BaseEntity], Serializer] = {
        StraightRoad: Serializer(
            lambda e: {"direction": e.direction.name},
            lambda d: StraightRoad(
                Direction[d.get("direction", "N")]
            ),
        ),
        ...
    }
    ```
] <code:serializerRegistry>

`CLASS_MAP` (@code:classMap) используется для обратного преобразования: по
строковому имени класса (например, `"StraightRoad"`) получается соответствующий
класс Python.

#figure(caption: [Карта классов])[
    ```Python
    CLASS_MAP: dict[str, type[BaseEntity]] = {
        cls.__name__: cls
        for cls in SERIALIZERS
    }
    ```
] <code:classMap>

=== Сериализация сущности

Функция `serializeEntity` (@code:serializeEntity) принимает сущность и
возвращает словарь с четырьмя полями:
- Тип сущности
- X клетки
- Y клетки
- Данные необходимые для инициализации - результат работы `serialize`

Если для типа нет сериализатора, выбрасывается исключение.

#figure(caption: [Функция `serializeEntity`])[
    ```Python
    def serializeEntity(entity: BaseEntity) -> dict:
        serializer = SERIALIZERS.get(type(entity))
        if not serializer:
            raise ValueError(f"No serializer for {type(entity).__name__}")

        return {
            "type": type(entity).__name__,
            "x": entity.cell.x(),
            "y": entity.cell.y(),
            "data": serializer.serialize(entity),
        }
    ```
] <code:serializeEntity>

=== Десериализация сущности

`deserializeEntity` (@code:deserializeEntity) выполняет обратное преобразование:
по полю `"type"` определяется класс, извлекается соответствующий сериализатор,
создаётся объект без позиции (через `deserialize`), а затем позиция
устанавливается отдельным вызовом `setCell`.

#figure(caption: [Функция `deserializeEntity`])[
    ```Python
    def deserializeEntity(entityData: dict[str, Any]) -> BaseEntity:
        cls = CLASS_MAP[entityData["type"]]
        serializer = SERIALIZERS.get(cls)

        if not serializer:
            raise ValueError(f"No deserializer for {cls.__name__}")

        obj = serializer.deserialize(entityData.get("data", {}))
        obj.setCell(QPoint(entityData["x"], entityData["y"]))

        return obj
    ```
] <code:deserializeEntity>

=== Сохранение сцены

`saveWorld` (@code:saveWorld) собирает все сущности со сцены, сериализует каждую
через `serializeEntity` и записывает JSON-объект с корневым полем `"entities"` в
указанный файл.


#figure(caption: [Функция `saveWorld`])[
    ```Python
    def saveWorld(world: World, path: str) -> None:
        entities = [
            serializeEntity(entity)
            for entity in world.entities()
        ]

        with open(path, "w", encoding="utf-8") as f:
            json.dump({"entities": entities}, f, indent=2)
    ```
] <code:saveWorld>

=== Загрузка сцены

`loadWorld` (@code:loadWorld) открывает JSON-файл, очищает текущую сцену и
добавляет каждую десериализованную сущность на сцену.

#figure(caption: [Функция `loadWorld`])[
    ```Python
    def loadWorld(world: World, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            worldData = json.load(f)

        world.clear()

        for entity in worldData["entities"]:
            world.addItem(deserializeEntity(entity))
    ```
] <code:loadWorld>

== Создание главного окна

`MainWindow` наследуется от `QMainWindow` и выступает контроллером приложения,
связывая сцену, панели управления и пользовательские действия.
=== Настройка окна

Метод `setupWindow` (@code:setupWindow) задаёт заголовок, размеры окна, и
размечает меню приложения.

#figure(caption: [Настройка окна])[
    ```Python
    def setupWindow(self) -> None:
        self.setWindowTitle("ИИС Дорожной системы")
        self.resize(1100, 700)

        menu = self.menuBar().addMenu("Файл")
        menu.addAction("Сохранить").triggered.connect(self.save)
        menu.addAction("Загрузить").triggered.connect(self.load)

        self.menuBar().addAction("События").triggered.connect(
            self.openEventsWindow
        )
    ```
] <code:setupWindow>

=== Компоновка интерфейса

`setupLayout` (@code:setupLayout) создаёт сцену (`World`) и помещает её в
центральный виджет (`WorldView`). Слева добавляется панель управления
(`ControlPanel`), справа — панель свойств (`PropertiesPanel`).

Здесь также настраиваются сигналы: клик по клетке вызывает добавление сущности,
выбор объекта обновляет панель свойств, а действия с панели управления управляют
режимом светофоров и добавлением машин на сцену.

#figure(caption: [Компоновка интерфейса])[
    ```Python
    def setupLayout(self) -> None:
        self.world = World()
        self.world.onWorldCellClicked.connect(self.onWorldCellClicked)
        self.world.selectionChanged.connect(self.onSelectionChanged)
        self.setCentralWidget(WorldView(self.world))

        self.controlPanel = ControlPanel(self)
        self.controlPanel.entityFactorySelected.connect(
            self.onFactorySelected
        )
        self.controlPanel.spawnCarsClicked.connect(self.onSpawnCarsClicked)
        self.controlPanel.tlModeChanged.connect(self.onTlModeChanged)
        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            self.controlPanel
        )

        self.propertiesPanel = PropertiesPanel()
        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea,
            self.propertiesPanel
        )
    ```
] <code:setupLayout>

=== Сохранение и загрузка

Методы `save` и `load` (листинг 6) открывают диалог выбора файла и вызывают
утилиты `saveWorld` / `loadWorld`, которые сериализуют состояние сцены в JSON и
восстанавливают его оттуда.

#figure(caption: [Методы сохранения и загрузки])[
    ```Python
    def save(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить", "", "JSON (*.json)"
        )
        if path:
            saveWorld(self.world, path)

    def load(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "", "Загрузить", "JSON (*.json)"
        )
        if path:
            loadWorld(self.world, path)
    ```
] <code:saveLoad>

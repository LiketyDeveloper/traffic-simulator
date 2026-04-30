== Создание точки входа

Точка входа — минимальный скрипт, который создаёт приложение и главное окно
(@code:entryPoint).

Точка входа -- скрипт, который инициализирует Qt-приложение и создаёт главное
окно. Передача `sys.argv` в `QApplication` позволяет обрабатывать аргументы
командной строки, а вызов `exec()` запускает цикл обработки событий.

#figure(
    caption: [Точка входа в приложение],
)[
    ```Python
    import sys
    from PySide6.QtWidgets import QApplication
    from src.window import MainWindow

    if __name__ == "__main__":
        app = QApplication(sys.argv)
        main_window = MainWindow(app)
        main_window.show()
        app.exec()
    ```
] <code:entryPoint>

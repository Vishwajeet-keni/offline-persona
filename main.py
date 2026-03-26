import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.character_dialog import CharacterDialog


def main():
    app = QApplication(sys.argv)

    # load stylesheet
    with open("ui/style.qss", "r") as f:
        app.setStyleSheet(f.read())

    while True:
        dialog = CharacterDialog()
        if dialog.exec():
            character = dialog.selected_character
            history = dialog.selected_history
            if character:
                window = MainWindow(character, history)
                window.show()
                app.exec()
        else:
            break


if __name__ == "__main__":
    main()

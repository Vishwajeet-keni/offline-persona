from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QLineEdit, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from core.character import list_characters, load_character, create_character, save_character
from core.storage import select_history, load_history


class CharacterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.selected_character = None
        self.selected_history = None

        self.setWindowTitle("OfflinePersona")
        self.setMinimumSize(400, 500)

        self._build_ui()
        self._load_characters()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("OfflinePersona")
        title.setObjectName("characterLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Select a character or create a new one")
        subtitle.setObjectName("roleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # character list
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._select_character)
        layout.addWidget(self.list_widget)

        # buttons
        btn_row = QHBoxLayout()

        select_btn = QPushButton("Select")
        select_btn.setObjectName("sendButton")
        select_btn.clicked.connect(self._select_character)

        create_btn = QPushButton("Create New")
        create_btn.clicked.connect(self._show_create_form)

        btn_row.addWidget(create_btn)
        btn_row.addWidget(select_btn)
        layout.addLayout(btn_row)

        # create form (hidden by default)
        self.form_widget = QDialog(self)
        self.form_widget.setWindowTitle("Create Character")
        self.form_widget.setMinimumSize(380, 320)

        form_layout = QVBoxLayout(self.form_widget)
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Alex")

        self.personality_input = QLineEdit()
        self.personality_input.setPlaceholderText("e.g. witty, sarcastic, calm")

        self.role_input = QLineEdit()
        self.role_input.setPlaceholderText("e.g. study buddy, mentor")

        self.backstory_input = QLineEdit()
        self.backstory_input.setPlaceholderText("e.g. A 20 year old CS student...")

        form.addRow("Name:", self.name_input)
        form.addRow("Personality:", self.personality_input)
        form.addRow("Role:", self.role_input)
        form.addRow("Backstory:", self.backstory_input)

        save_btn = QPushButton("Save Character")
        save_btn.setObjectName("sendButton")
        save_btn.clicked.connect(self._save_new_character)

        form_layout.addLayout(form)
        form_layout.addWidget(save_btn)

    def _load_characters(self):
        self.list_widget.clear()
        characters = list_characters()
        if not characters:
            self.list_widget.addItem("No characters yet — create one!")
        else:
            for name in characters:
                self.list_widget.addItem(name.capitalize())

    def _select_character(self):
        item = self.list_widget.currentItem()
        if not item or item.text().startswith("No characters"):
            return

        name = item.text().lower()
        character = load_character(name)
        if not character:
            return

        self.selected_character = character

        # ask about history
        histories = self._get_histories(name)
        if histories:
            history_dialog = HistoryDialog(name, histories, self)
            if history_dialog.exec():
                self.selected_history = history_dialog.selected_history
            else:
                self.selected_history = None
        else:
            self.selected_history = None

        self.accept()

    def _get_histories(self, character_name):
        import os
        HISTORY_DIR = "histories"
        if not os.path.exists(HISTORY_DIR):
            return []
        return sorted([
            f for f in os.listdir(HISTORY_DIR)
            if f.startswith(character_name.lower()) and f.endswith(".json")
        ], reverse=True)

    def _show_create_form(self):
        self.name_input.clear()
        self.personality_input.clear()
        self.role_input.clear()
        self.backstory_input.clear()
        self.form_widget.exec()

    def _save_new_character(self):
        name = self.name_input.text().strip()
        personality = self.personality_input.text().strip()
        role = self.role_input.text().strip()
        backstory = self.backstory_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Missing Field", "Name is required.")
            return

        character = {
            "name": name,
            "personality": personality,
            "role": role,
            "backstory": backstory
        }
        save_character(character)
        self.form_widget.close()
        self._load_characters()


class HistoryDialog(QDialog):
    def __init__(self, character_name, histories, parent=None):
        super().__init__(parent)
        self.histories = histories
        self.selected_history = None

        self.setWindowTitle("Load Previous Conversation?")
        self.setMinimumSize(360, 300)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        label = QLabel(f"Previous conversations with {character_name.capitalize()}:")
        label.setObjectName("roleLabel")
        layout.addWidget(label)

        self.list_widget = QListWidget()
        for h in histories:
            self.list_widget.addItem(h.replace(".json", "").replace("_", " "))
        layout.addWidget(self.list_widget)

        btn_row = QHBoxLayout()

        load_btn = QPushButton("Load")
        load_btn.setObjectName("sendButton")
        load_btn.clicked.connect(self._load_selected)

        fresh_btn = QPushButton("Start Fresh")
        fresh_btn.clicked.connect(self.reject)

        btn_row.addWidget(fresh_btn)
        btn_row.addWidget(load_btn)
        layout.addLayout(btn_row)

    def _load_selected(self):
        item = self.list_widget.currentItem()
        if not item:
            self.reject()
            return

        index = self.list_widget.currentRow()
        filename = self.histories[index]

        from core.storage import load_history
        self.selected_history = load_history(filename)
        self.accept()

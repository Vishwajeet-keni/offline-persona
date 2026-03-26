from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QKeyEvent
import ollama


class ChatWorker(QThread):
    response_ready = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, model, history):
        super().__init__()
        self.model = model
        self.history = history

    def run(self):
        try:
            response = ollama.chat(model=self.model, messages=self.history)
            reply = response["message"]["content"]
            self.response_ready.emit(reply)
        except Exception as e:
            self.error.emit(str(e))


class InputBox(QTextEdit):
    submit = pyqtSignal()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.submit.emit()
        else:
            super().keyPressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self, character, history=None):
        super().__init__()
        self.character = character
        self.history = history or []
        self.model = "gemma2:2b"

        self.setWindowTitle("OfflinePersona")
        self.setMinimumSize(700, 550)

        self._build_ui()
        self._inject_system_prompt()

        if self.history:
            self._reload_history()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        # Top bar
        top = QHBoxLayout()
        info = QVBoxLayout()

        self.char_label = QLabel(self.character["name"])
        self.char_label.setObjectName("characterLabel")

        self.role_label = QLabel(self.character["role"])
        self.role_label.setObjectName("roleLabel")

        info.addWidget(self.char_label)
        info.addWidget(self.role_label)

        switch_btn = QPushButton("Switch Character")
        switch_btn.clicked.connect(self._switch_character)

        top.addLayout(info)
        top.addStretch()
        top.addWidget(switch_btn)
        layout.addLayout(top)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setObjectName("chatDisplay")
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        # Input row
        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        self.mic_btn = QPushButton("🎤")
        self.mic_btn.setObjectName("micButton")
        self.mic_btn.setFixedSize(44, 44)
        self.mic_btn.setToolTip("Hold to speak (coming soon)")

        self.input_box = InputBox()
        self.input_box.setObjectName("inputBox")
        self.input_box.setFixedHeight(44)
        self.input_box.setPlaceholderText("Type a message... (Enter to send, Shift+Enter for newline)")
        self.input_box.submit.connect(self._send_message)

        self.send_btn = QPushButton("Send")
        self.send_btn.setObjectName("sendButton")
        self.send_btn.setFixedHeight(44)
        self.send_btn.clicked.connect(self._send_message)

        input_row.addWidget(self.mic_btn)
        input_row.addWidget(self.input_box)
        input_row.addWidget(self.send_btn)
        layout.addLayout(input_row)

    def _inject_system_prompt(self):
        if not any(m["role"] == "system" for m in self.history):
            system_prompt = f"""You are {self.character['name']}.
Personality: {self.character['personality']}
Role: {self.character['role']}
Backstory: {self.character['backstory']}
Stay in character at all times."""
            self.history.insert(0, {"role": "system", "content": system_prompt})

    def _reload_history(self):
        for msg in self.history:
            if msg["role"] == "user":
                self._append_message("You", msg["content"])
            elif msg["role"] == "assistant":
                self._append_message(self.character["name"], msg["content"])

    def _append_message(self, sender, text):
        if sender == "You":
            color = "#89b4fa"
        elif sender == self.character["name"]:
            color = "#a6e3a1"
        else:
            color = "#6c7086"

        self.chat_display.append(
            f'<p><span style="color:{color};font-weight:bold;">{sender}</span><br>{text}</p>'
        )

    def _send_message(self):
        text = self.input_box.toPlainText().strip()
        if not text:
            return

        self.input_box.clear()
        self._append_message("You", text)
        self.history.append({"role": "user", "content": text})

        self.send_btn.setEnabled(False)
        self.input_box.setEnabled(False)
        self._append_message("...", "thinking...")

        self.worker = ChatWorker(self.model, self.history)
        self.worker.response_ready.connect(self._on_response)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_response(self, reply):
        # remove "thinking..." message
        cursor = self.chat_display.textCursor()
        self.chat_display.undo()

        self.history.append({"role": "assistant", "content": reply})
        self._append_message(self.character["name"], reply)

        self.send_btn.setEnabled(True)
        self.input_box.setEnabled(True)
        self.input_box.setFocus()

    def _on_error(self, error):
        self._append_message("Error", error)
        self.send_btn.setEnabled(True)
        self.input_box.setEnabled(True)

    def _switch_character(self):
        from core.storage import save_history
        save_history(self.character["name"], self.history)
        self.close()

    def closeEvent(self, event):
        from core.storage import save_history
        save_history(self.character["name"], self.history)
        event.accept()

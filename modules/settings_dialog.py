from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QCheckBox,
    QSpinBox,
)


class SettingsDialog(QDialog):

    def __init__(self, settings, parent=None):
        super().__init__(parent)

        self.settings = settings.copy()

        self.setWindowTitle("Preferences")
        self.resize(350, 250)

        layout = QVBoxLayout(self)

        # Default qubits

        row = QHBoxLayout()

        row.addWidget(QLabel("Default Qubits"))

        self.qubits = QComboBox()
        self.qubits.addItems(["1", "2", "3", "4", "5"])
        self.qubits.setCurrentText(str(self.settings["default_qubits"]))

        row.addWidget(self.qubits)

        layout.addLayout(row)

        # Animation speed

        row = QHBoxLayout()

        row.addWidget(QLabel("Animation Speed (ms)"))

        self.speed = QSpinBox()
        self.speed.setRange(100, 3000)
        self.speed.setSingleStep(100)
        self.speed.setValue(self.settings["animation_speed"])

        row.addWidget(self.speed)

        layout.addLayout(row)

        # Autosave

        self.autosave = QCheckBox("Enable Autosave")
        self.autosave.setChecked(self.settings["autosave"])

        layout.addWidget(self.autosave)

        # Theme

        row = QHBoxLayout()

        row.addWidget(QLabel("Theme"))

        self.theme = QComboBox()
        self.theme.addItems(
            [
                "Light",
                "Dark",
                "System",
            ]
        )

        self.theme.setCurrentText(
            self.settings.get(
                "theme",
                "Light",
            )
        )

        row.addWidget(self.theme)

        layout.addLayout(row)

        layout.addStretch()

        buttons = QHBoxLayout()

        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        buttons.addStretch()
        buttons.addWidget(self.save_button)
        buttons.addWidget(self.cancel_button)

        layout.addLayout(buttons)

        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_settings(self):

        return {
            "default_qubits": int(self.qubits.currentText()),
            "animation_speed": self.speed.value(),
            "autosave": self.autosave.isChecked(),
            "theme": self.theme.currentText(),
        }

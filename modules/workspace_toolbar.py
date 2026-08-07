from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton


class WorkspaceToolbar(QWidget):

    view_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)

        self.buttons = {}

        views = [
            "Circuit",
            "Histogram",
            "Statevector",
            "Probability",
            "Bloch Sphere",
            "Console",
            "Statistics",
        ]

        for view in views:

            button = QPushButton(view)

            button.setCheckable(True)

            button.clicked.connect(lambda checked, v=view: self.view_requested.emit(v))

            layout.addWidget(button)

            self.buttons[view] = button

        layout.addStretch()

    def set_active(self, view, active):

        if view in self.buttons:
            self.buttons[view].setChecked(active)

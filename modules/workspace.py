from PySide6.QtWidgets import QWidget, QVBoxLayout

from modules.workspace_toolbar import WorkspaceToolbar


class Workspace(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        layout = QVBoxLayout(self)

        self.toolbar = WorkspaceToolbar()

        layout.addWidget(self.toolbar)

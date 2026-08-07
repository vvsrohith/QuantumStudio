from PySide6.QtWidgets import QMainWindow


class DetachableWindow(QMainWindow):

    def __init__(self, title="Window"):
        super().__init__()

        self.setWindowTitle(title)
        self.resize(800, 600)

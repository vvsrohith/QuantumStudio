from PySide6.QtWidgets import QMainWindow, QTextEdit


class ConsoleWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Console")
        self.resize(600, 400)

        self.text = QTextEdit()
        self.text.setReadOnly(True)

        self.setCentralWidget(self.text)

    def write(self, msg):
        self.text.append(msg)

from PySide6.QtWidgets import QMainWindow, QTextEdit


class StatisticsWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Statistics")
        self.resize(400, 300)

        self.text = QTextEdit()
        self.setCentralWidget(self.text)

    def update_stats(self, data):
        self.text.setText(data)

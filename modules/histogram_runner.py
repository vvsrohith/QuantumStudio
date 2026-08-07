from PySide6.QtWidgets import QMainWindow


class HistogramWindow(QMainWindow):

    def __init__(self, histogram_widget, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Histogram")
        self.resize(900, 650)

        self.setCentralWidget(histogram_widget)

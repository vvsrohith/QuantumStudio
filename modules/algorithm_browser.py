import importlib

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QHBoxLayout,
    QTextEdit,
    QSplitter,
)


class AlgorithmBrowser(QDialog):

    def __init__(self, algorithms, parent=None):
        super().__init__(parent)

        self.algorithms = algorithms

        self.setWindowTitle("Quantum Algorithm Library")
        self.resize(700, 500)

        layout = QVBoxLayout(self)

        title = QLabel("Quantum Algorithm Library")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:16px;font-weight:bold;")
        layout.addWidget(title)

        layout.addWidget(QLabel("Search"))

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search algorithms...")
        layout.addWidget(self.search)

        splitter = QSplitter()

        self.list = QListWidget()

        self.details = QTextEdit()
        self.details.setReadOnly(True)

        splitter.addWidget(self.list)
        splitter.addWidget(self.details)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)

        button_layout = QHBoxLayout()

        self.load_button = QPushButton("Load")
        self.cancel_button = QPushButton("Cancel")

        button_layout.addStretch()
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.populate()

        self.search.textChanged.connect(self.filter)
        self.list.currentTextChanged.connect(self.show_details)

        self.load_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        self.list.itemDoubleClicked.connect(lambda: self.accept())

    def populate(self):

        self.list.clear()

        for name in sorted(self.algorithms.keys()):
            self.list.addItem(name)

        if self.list.count():
            self.list.setCurrentRow(0)

    def filter(self, text):

        self.list.clear()

        text = text.lower()

        for name in sorted(self.algorithms.keys()):
            if text in name.lower():
                self.list.addItem(name)

        if self.list.count():
            self.list.setCurrentRow(0)

    def show_details(self, name):

        module = self.algorithms.get(name)

        if module is None:
            self.details.clear()
            return

        try:

            imported = importlib.import_module(f"algorithms.{module}")

            info = getattr(imported, "INFO", {})

            circuit = imported.build()

            html = f"""
            <h2>{info.get("name", name)}</h2>

            <p>{info.get("description", "")}</p>

            <hr>

            <p><b>Qubits:</b> {circuit.num_qubits}</p>

            <p><b>Depth:</b> {circuit.depth()}</p>

            <p><b>Gate Count:</b> {len(circuit.data)}</p>
            """

            self.details.setHtml(html)

        except Exception as e:

            self.details.setPlainText(str(e))

    def selected_algorithm(self):

        item = self.list.currentItem()

        if item is not None:
            return item.text()

        return None

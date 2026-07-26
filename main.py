import sys

from PySide6.QtWidgets import QApplication

from ui import QuantumStudio
from theme import apply_theme


if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    apply_theme(
        app
    )

    window = QuantumStudio()

    window.show()

    sys.exit(
        app.exec()
    )
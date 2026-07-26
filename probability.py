from PySide6.QtWidgets import QTextEdit


class ProbabilityCanvas(QTextEdit):

    def __init__(self):

        super().__init__()

        self.setReadOnly(True)

    def update_probabilities(self, probabilities):

        text = "Basis State\tProbability\n"
        text += "-" * 30 + "\n"

        for state, probability in sorted(probabilities.items()):

            text += f"{str(state)}\t{float(probability) * 100:.2f}%\n"

        self.setPlainText(text)

    def clear(self):

        self.setPlainText("")
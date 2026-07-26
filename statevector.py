from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class StatevectorCanvas(FigureCanvasQTAgg):

    def __init__(self):

        self.figure = Figure(figsize=(6, 4))

        super().__init__(self.figure)

        self.axes = self.figure.add_subplot(111)

    def update_state(self, statevector):

        self.axes.clear()

        probabilities = statevector.probabilities()

        labels = [
            format(i, f"0{statevector.num_qubits}b")
            for i in range(len(probabilities))
        ]

        self.axes.bar(
            labels,
            probabilities
        )

        self.axes.set_ylim(0, 1)
        self.axes.set_title("Statevector Probabilities")
        self.axes.set_xlabel("Basis State")
        self.axes.set_ylabel("Probability")

        self.draw()

    def clear(self):

        self.axes.clear()

        self.draw()
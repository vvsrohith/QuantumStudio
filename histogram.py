from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class HistogramCanvas(FigureCanvasQTAgg):

    def __init__(self):

        self.figure = Figure(figsize=(6, 4))

        super().__init__(self.figure)

        self.axes = self.figure.add_subplot(111)

    def update_plot(self, counts):

        self.axes.clear()

        if counts:

            total = sum(counts.values())

            states = []
            probabilities = []

            for state, value in counts.items():

                if isinstance(state, str) and state.startswith("0x"):

                    binary = bin(int(state, 16))[2:].zfill(2)

                else:
                    binary = state

                states.append("|" + binary + "⟩")

                probabilities.append((value / total) * 100)

            self.axes.bar(states, probabilities)

            self.axes.set_ylabel("Probability (%)")

            self.axes.set_xlabel("Quantum States")

            self.axes.set_ylim(0, 100)

            for i, value in enumerate(probabilities):

                self.axes.text(i, value + 2, f"{value:.1f}%", ha="center")

        self.draw()

    def clear(self):

        self.axes.clear()

        self.draw()

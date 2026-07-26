from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from qiskit.visualization import plot_histogram


class HistogramCanvas(FigureCanvasQTAgg):

    def __init__(self):

        self.figure = Figure(figsize=(6, 4))

        super().__init__(self.figure)

        self.axes = self.figure.add_subplot(111)

    def update_plot(self, counts):

        self.axes.clear()

        if counts:

            plot_histogram(
                counts,
                ax=self.axes
            )

        self.draw()

    def clear(self):

        self.axes.clear()

        self.draw()
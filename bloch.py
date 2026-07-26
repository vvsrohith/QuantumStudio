from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
from qiskit.quantum_info import DensityMatrix


class BlochCanvas(FigureCanvasQTAgg):

    def __init__(self):

        self.figure = Figure(figsize=(6, 6))

        super().__init__(self.figure)

    def update_state(self, statevector):

        self.figure.clear()

        num_qubits = statevector.num_qubits

        for q in range(num_qubits):

            ax = self.figure.add_subplot(
                1,
                num_qubits,
                q + 1,
                projection="3d"
            )

            u = np.linspace(0, 2 * np.pi, 60)
            v = np.linspace(0, np.pi, 60)

            x = np.outer(np.cos(u), np.sin(v))
            y = np.outer(np.sin(u), np.sin(v))
            z = np.outer(np.ones(np.size(u)), np.cos(v))

            ax.plot_surface(
                x,
                y,
                z,
                alpha=0.1
            )

            rho = DensityMatrix(statevector)

            from qiskit.quantum_info import partial_trace

            reduced = partial_trace(
                rho,
                [i for i in range(num_qubits) if i != q]
            )

            mat = reduced.data

            bx = np.real(np.trace(mat @ np.array([[0, 1],
                                      [1, 0]])))

            by = np.real(np.trace(mat @ np.array([[0, -1j],
                                      [1j, 0]])))

            bz = np.real(np.trace(mat @ np.array([[1, 0],
                                      [0, -1]])))

            ax.quiver(
                0,
                0,
                0,
                bx,
                by,
                bz,
                color="red",
                linewidth=4,
                arrow_length_ratio=0.15
            )

            ax.set_xlim([-1, 1])
            ax.set_ylim([-1, 1])
            ax.set_zlim([-1, 1])

            ax.set_title(f"Qubit {q}")

        self.draw()

    def clear(self):

        self.figure.clear()

        self.draw()
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
from qiskit.quantum_info import DensityMatrix, partial_trace


class BlochCanvas(FigureCanvasQTAgg):

    def __init__(self):

        self.figure = Figure(figsize=(6, 6))

        super().__init__(self.figure)

    def update_state(self, statevector):

        self.figure.clear()

        num_qubits = statevector.num_qubits

        rho = DensityMatrix(statevector)

        sigma_x = np.array([[0, 1], [1, 0]])

        sigma_y = np.array([[0, -1j], [1j, 0]])

        sigma_z = np.array([[1, 0], [0, -1]])

        for q in range(num_qubits):

            ax = self.figure.add_subplot(1, num_qubits, q + 1, projection="3d")

            u = np.linspace(0, 2 * np.pi, 50)

            v = np.linspace(0, np.pi, 50)

            x = np.outer(np.cos(u), np.sin(v))

            y = np.outer(np.sin(u), np.sin(v))

            z = np.outer(np.ones(len(u)), np.cos(v))

            ax.plot_surface(x, y, z, alpha=0.1)

            reduced = partial_trace(rho, [i for i in range(num_qubits) if i != q])

            mat = reduced.data

            bx = np.real(np.trace(mat @ sigma_x))

            by = np.real(np.trace(mat @ sigma_y))

            bz = np.real(np.trace(mat @ sigma_z))

            ax.quiver(0, 0, 0, bx, by, bz, linewidth=3, arrow_length_ratio=0.15)
            ax.set_xlim([-1.2, 1.2])
            ax.set_ylim([-1.2, 1.2])
            ax.set_zlim([-1.2, 1.2])

            ax.set_box_aspect([1, 1, 1])

            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_zlabel("Z")

            ax.set_title(f"Qubit {q}")
            if abs(bx) < 0.01 and abs(by) < 0.01 and abs(bz) < 0.01:
                ax.text(0, 0, 0, "Mixed\nState", ha="center")

        self.draw()

    def clear(self):

        self.figure.clear()

        self.draw()

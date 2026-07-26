from algorithms.bell import BellState

from qiskit_aer import AerSimulator

from qiskit.visualization import plot_histogram

import matplotlib.pyplot as plt


backend = AerSimulator()

circuit = BellState.build()

job = backend.run(
    circuit,
    shots=1024
)

result = job.result()

counts = result.get_counts()

print(counts)

plot_histogram(counts)

plt.show()
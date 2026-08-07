INFO = {
    "name": "Grover Search",
    "description": "Searches an unsorted database using amplitude amplification to achieve quadratic speedup.",
}
from qiskit import QuantumCircuit

DISPLAY_NAME = "Grover Search"


def build():
    circuit = QuantumCircuit(2, 2)

    # Superposition
    circuit.h(0)
    circuit.h(1)

    # Oracle
    circuit.cz(0, 1)

    # Diffusion Operator
    circuit.h(0)
    circuit.h(1)

    circuit.x(0)
    circuit.x(1)

    circuit.h(1)
    circuit.cx(0, 1)
    circuit.h(1)

    circuit.x(0)
    circuit.x(1)

    circuit.h(0)
    circuit.h(1)

    circuit.measure(0, 0)
    circuit.measure(1, 1)

    return circuit

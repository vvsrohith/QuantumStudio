INFO = {
    "name": "Deutsch Algorithm",
    "description": "Determines whether a one-bit Boolean function is constant or balanced with a single oracle query.",
}

from qiskit import QuantumCircuit

DISPLAY_NAME = "Deutsch"


def build():
    circuit = QuantumCircuit(2, 1)

    circuit.x(1)

    circuit.h(0)
    circuit.h(1)

    circuit.cx(0, 1)

    circuit.h(0)

    circuit.measure(0, 0)

    return circuit

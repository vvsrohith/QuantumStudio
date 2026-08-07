INFO = {
    "name": "Quantum Teleportation",
    "description": "Transfers an unknown quantum state between two distant qubits using entanglement and classical communication.",
}
from qiskit import QuantumCircuit

DISPLAY_NAME = "Teleportation"


def build():
    circuit = QuantumCircuit(3, 2)

    circuit.h(1)
    circuit.cx(1, 2)

    circuit.cx(0, 1)
    circuit.h(0)

    circuit.measure(0, 0)
    circuit.measure(1, 1)

    circuit.cx(1, 2)
    circuit.cz(0, 2)

    return circuit

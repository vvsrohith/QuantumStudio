from qiskit import QuantumCircuit

DISPLAY_NAME = "GHZ State"


def build():
    circuit = QuantumCircuit(3)

    circuit.h(0)
    circuit.cx(0, 1)
    circuit.cx(1, 2)

    return circuit

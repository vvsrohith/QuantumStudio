INFO = {
    "name": "Bell State",
    "description": "Creates a maximally entangled Bell pair using a Hadamard gate followed by a CNOT gate.",
}
from qiskit import QuantumCircuit

DISPLAY_NAME = "Bell State"


def build():
    circuit = QuantumCircuit(2, 2)

    circuit.h(0)
    circuit.cx(0, 1)

    circuit.measure(0, 0)
    circuit.measure(1, 1)

    return circuit

INFO = {
    "name": "Quantum Fourier Transform",
    "description": "Performs the quantum analogue of the discrete Fourier transform and is a key component of many quantum algorithms.",
}
from qiskit import QuantumCircuit

DISPLAY_NAME = "Quantum Fourier Transform"


def build():
    circuit = QuantumCircuit(3)

    circuit.h(0)

    circuit.cz(1, 0)
    circuit.cz(2, 0)

    circuit.h(1)

    circuit.cz(2, 1)

    circuit.h(2)

    circuit.swap(0, 2)

    return circuit

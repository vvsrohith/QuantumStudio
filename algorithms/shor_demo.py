from qiskit import QuantumCircuit

from algorithms.qft import QuantumFourierTransform


class ShorDemo:

    @staticmethod
    def build(qubits=4):

        if qubits < 3:
            raise ValueError(
                "Use at least 3 qubits."
            )

        circuit = QuantumCircuit(
            qubits,
            qubits
        )

        # Prepare a periodic state
        for qubit in range(qubits):

            circuit.h(qubit)

        # Simple periodic phase pattern
        circuit.cz(0, 1)

        if qubits > 2:
            circuit.cz(1, 2)

        if qubits > 3:
            circuit.cz(2, 3)

        # Apply Quantum Fourier Transform
        QuantumFourierTransform.apply(
            circuit,
            qubits
        )

        # Measure
        circuit.measure(
            range(qubits),
            range(qubits)
        )

        return circuit

    @staticmethod
    def name():

        return "Shor Algorithm Demo"

    @staticmethod
    def description():

        return (
            "Educational demonstration of the "
            "period-finding stage used in "
            "Shor's factoring algorithm."
        )

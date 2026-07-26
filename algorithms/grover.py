from math import floor, pi, sqrt

from qiskit import QuantumCircuit


class GroverSearch:

    @staticmethod
    def build(qubits=2, marked_state=None):

        if qubits < 2:
            raise ValueError(
                "Grover Search requires at least 2 qubits."
            )

        if marked_state is None:
            marked_state = "1" * qubits

        circuit = QuantumCircuit(
            qubits,
            qubits
        )

        # Create uniform superposition
        for qubit in range(qubits):
            circuit.h(qubit)

        iterations = max(
            1,
            floor(
                (pi / 4) * sqrt(2 ** qubits)
            )
        )

        for _ in range(iterations):

            GroverSearch.oracle(
                circuit,
                marked_state
            )

            GroverSearch.diffuser(
                circuit,
                qubits
            )

        circuit.measure(
            range(qubits),
            range(qubits)
        )

        return circuit

    @staticmethod
    def oracle(
        circuit,
        marked_state
    ):

        qubits = len(marked_state)

        for i, bit in enumerate(marked_state):

            if bit == "0":
                circuit.x(i)

        circuit.h(qubits - 1)

        circuit.mcx(
            list(range(qubits - 1)),
            qubits - 1
        )

        circuit.h(qubits - 1)

        for i, bit in enumerate(marked_state):

            if bit == "0":
                circuit.x(i)

    @staticmethod
    def diffuser(
        circuit,
        qubits
    ):

        for qubit in range(qubits):
            circuit.h(qubit)
            circuit.x(qubit)

        circuit.h(qubits - 1)

        circuit.mcx(
            list(range(qubits - 1)),
            qubits - 1
        )

        circuit.h(qubits - 1)

        for qubit in range(qubits):
            circuit.x(qubit)
            circuit.h(qubit)

    @staticmethod
    def name():

        return "Grover Search"

    @staticmethod
    def description():

        return (
            "Searches an unsorted database using "
            "Grover's amplitude amplification algorithm."
        )
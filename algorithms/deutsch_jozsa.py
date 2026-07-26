from qiskit import QuantumCircuit


class DeutschJozsa:

    @staticmethod
    def build(n=3, oracle="balanced"):

        circuit = QuantumCircuit(
            n + 1,
            n
        )

        # Prepare ancilla
        circuit.x(n)

        # Superposition
        for qubit in range(n + 1):
            circuit.h(qubit)

        # Oracle
        if oracle == "balanced":

            for qubit in range(n):
                circuit.cx(
                    qubit,
                    n
                )

        elif oracle == "constant_1":

            circuit.x(n)

        elif oracle == "constant_0":

            pass

        else:

            raise ValueError(
                "Oracle must be 'balanced', 'constant_0', or 'constant_1'."
            )

        # Interference
        for qubit in range(n):
            circuit.h(qubit)

        # Measurement
        circuit.measure(
            range(n),
            range(n)
        )

        return circuit

    @staticmethod
    def name():

        return "Deutsch-Jozsa Algorithm"

    @staticmethod
    def description():

        return (
            "Determines whether an n-bit Boolean "
            "function is constant or balanced "
            "using a single oracle evaluation."
        )
from qiskit import QuantumCircuit


class DeutschAlgorithm:

    @staticmethod
    def build(oracle="balanced"):

        circuit = QuantumCircuit(
            2,
            1
        )

        # Prepare ancilla qubit
        circuit.x(1)

        # Create superposition
        circuit.h(0)
        circuit.h(1)

        # Oracle
        if oracle == "balanced":

            circuit.cx(
                0,
                1
            )

        elif oracle == "constant_1":

            circuit.x(1)

        elif oracle == "constant_0":

            pass

        else:

            raise ValueError(
                "Oracle must be 'balanced', 'constant_0', or 'constant_1'."
            )

        # Interference
        circuit.h(0)

        # Measurement
        circuit.measure(
            0,
            0
        )

        return circuit

    @staticmethod
    def name():

        return "Deutsch Algorithm"

    @staticmethod
    def description():

        return (
            "Determines whether a one-bit Boolean "
            "function is constant or balanced using "
            "a single oracle query."
        )
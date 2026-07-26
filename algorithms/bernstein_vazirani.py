from qiskit import QuantumCircuit


class BernsteinVazirani:

    @staticmethod
    def build(secret="1011"):

        n = len(secret)

        circuit = QuantumCircuit(
            n + 1,
            n
        )

        # Prepare ancilla
        circuit.x(n)

        # Create superposition
        for qubit in range(n + 1):
            circuit.h(qubit)

        # Oracle
        for index, bit in enumerate(secret):

            if bit == "1":

                circuit.cx(
                    index,
                    n
                )

        # Interference
        for qubit in range(n):
            circuit.h(qubit)

        # Measure
        circuit.measure(
            range(n),
            range(n)
        )

        return circuit

    @staticmethod
    def name():

        return "Bernstein-Vazirani Algorithm"

    @staticmethod
    def description():

        return (
            "Finds a hidden binary string using "
            "a single oracle query."
        )
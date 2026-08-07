INFO = {
    "name": "Superdense Coding",
    "description": "Transmits two classical bits by sending only one qubit using shared entanglement.",
}
from qiskit import QuantumCircuit


class SuperdenseCoding:

    @staticmethod
    def build(message="10"):

        circuit = QuantumCircuit(2, 2)

        # Create Bell pair
        circuit.h(0)
        circuit.cx(0, 1)

        # Encode message
        if message == "01":
            circuit.z(0)

        elif message == "10":
            circuit.x(0)

        elif message == "11":
            circuit.x(0)
            circuit.z(0)

        # Decode
        circuit.cx(0, 1)
        circuit.h(0)

        circuit.measure([0, 1], [0, 1])

        return circuit

    @staticmethod
    def name():

        return "Superdense Coding"

    @staticmethod
    def description():

        return "Encodes two classical bits into one qubit " "using entanglement."

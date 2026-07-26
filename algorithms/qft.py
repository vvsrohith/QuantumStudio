from math import pi

from qiskit import QuantumCircuit


class QuantumFourierTransform:

    @staticmethod
    def build(qubits=3):

        circuit = QuantumCircuit(
            qubits,
            qubits
        )

        QuantumFourierTransform.apply(
            circuit,
            qubits
        )

        circuit.measure(
            range(qubits),
            range(qubits)
        )

        return circuit

    @staticmethod
    def apply(
        circuit,
        qubits
    ):

        for target in range(qubits):

            circuit.h(target)

            for control in range(target + 1, qubits):

                angle = pi / (2 ** (control - target))

                circuit.cp(
                    angle,
                    control,
                    target
                )

        for i in range(qubits // 2):

            circuit.swap(
                i,
                qubits - i - 1
            )

    @staticmethod
    def inverse(
        circuit,
        qubits
    ):

        for i in range(qubits // 2):

            circuit.swap(
                i,
                qubits - i - 1
            )

        for target in reversed(range(qubits)):

            for control in reversed(range(target + 1, qubits)):

                angle = -pi / (2 ** (control - target))

                circuit.cp(
                    angle,
                    control,
                    target
                )

            circuit.h(target)

    @staticmethod
    def name():

        return "Quantum Fourier Transform"

    @staticmethod
    def description():

        return (
            "Applies the Quantum Fourier Transform "
            "or its inverse to a quantum register."
        )
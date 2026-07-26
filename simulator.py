from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator


class QuantumSimulator:

    def __init__(self, qubits=2):

        self.backend = AerSimulator()
        self.last_counts = {}

        self.create_circuit(qubits)

    def create_circuit(self, qubits):

        self.num_qubits = qubits

        self.circuit = QuantumCircuit(
            qubits,
            qubits
        )

    def reset(self):

        self.create_circuit(self.num_qubits)

    def h(self, q):
        self.circuit.h(q)

    def x(self, q):
        self.circuit.x(q)

    def y(self, q):
        self.circuit.y(q)

    def z(self, q):
        self.circuit.z(q)

    def s(self, q):
        self.circuit.s(q)

    def t(self, q):
        self.circuit.t(q)

    def rx(self, angle, q):
        self.circuit.rx(angle, q)

    def ry(self, angle, q):
        self.circuit.ry(angle, q)

    def rz(self, angle, q):
        self.circuit.rz(angle, q)

    def cx(self, control, target):
        self.circuit.cx(control, target)

    def cz(self, control, target):
        self.circuit.cz(control, target)

    def swap(self, q1, q2):
        self.circuit.swap(q1, q2)

    def measure_all(self):

        self.circuit.measure(
            range(self.num_qubits),
            range(self.num_qubits)
        )

    def get_statevector(self):

        temp = self.circuit.copy()

        temp.remove_final_measurements()

        state = Statevector.from_instruction(temp)

        return state

    def get_probabilities(self):

        state = self.get_statevector()

        probs = state.probabilities_dict()

        return probs

    def run(self, shots=1024):

        temp = self.circuit.copy()

        has_measure = any(
            instruction.operation.name == "measure"
            for instruction in temp.data
        )

        if not has_measure:

            temp.measure(
                range(self.num_qubits),
                range(self.num_qubits)
            )

        job = self.backend.run(
            temp,
            shots=shots
        )

        result = job.result()

        self.last_counts = result.get_counts()

        return self.last_counts

    def get_circuit(self):

        return self.circuit

    def depth(self):

        return self.circuit.depth()

    def width(self):

        return self.circuit.num_qubits

    def gate_count(self):

        return len(self.circuit.data)

    def clear_measurements(self):

        temp = self.circuit.copy()

        temp.remove_final_measurements()

        self.circuit = temp

    def qasm(self):

        try:
            return self.circuit.qasm()

        except Exception:
            return "OpenQASM export unavailable for this version."

    def get_counts(self):

        return self.last_counts

    def statevector(self):

        return self.get_statevector()

    def info(self):

        return {

            "qubits": self.width(),

            "depth": self.depth(),

            "gates": self.gate_count()
        }
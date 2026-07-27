from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector


class QuantumSimulator:

    def __init__(self, num_qubits=2):

        self.num_qubits = num_qubits

        self.backend = AerSimulator()

        self.create_circuit(num_qubits)

        self.last_result = None
        self.last_state = None

    def create_circuit(self, qubits):

        self.num_qubits = qubits

        self.circuit = QuantumCircuit(qubits, qubits)

    def reset(self):

        self.create_circuit(self.num_qubits)

        self.last_result = None
        self.last_state = None

    # Single qubit gates

    def h(self, qubit):

        self.circuit.h(qubit)

    def x(self, qubit):

        self.circuit.x(qubit)

    def y(self, qubit):

        self.circuit.y(qubit)

    def z(self, qubit):

        self.circuit.z(qubit)

    def s(self, qubit):

        self.circuit.s(qubit)

    def t(self, qubit):

        self.circuit.t(qubit)

    # Rotation gates

    def rx(self, angle, qubit):

        self.circuit.rx(angle, qubit)

    def ry(self, angle, qubit):

        self.circuit.ry(angle, qubit)

    def rz(self, angle, qubit):

        self.circuit.rz(angle, qubit)

    # Multi qubit gates

    def cx(self, control, target):

        self.circuit.cx(control, target)

    def cz(self, control, target):

        self.circuit.cz(control, target)

    def swap(self, q1, q2):

        self.circuit.swap(q1, q2)

    # Measurement
    def measure_all(self):

        self.circuit.measure(
            range(self.num_qubits),
            range(self.num_qubits),
        )

    # Execute

    def run(self):

        try:
            self.last_state = Statevector(
                self.circuit.remove_final_measurements(inplace=False)
            )
        except Exception:
            self.last_state = None

        print("\n===== CIRCUIT =====")
        print(self.circuit.draw())

        job = self.backend.run(self.circuit, shots=1024)
        self.last_result = job.result()

        print("\n===== RESULT DATA =====")
        print(self.last_result.data(0))

        return self.last_result  # Histogram data

    def get_counts(self):

        if self.last_result is None:
            return {}

        try:
            return self.last_result.get_counts()

        except Exception:
            data = self.last_result.data(0)

            if "counts" in data:
                return data["counts"]

            return {}

    def get_state(self):

        if self.last_state:

            return self.last_state

        return Statevector(self.circuit.remove_final_measurements(inplace=False))

    def statevector(self):

        return self.get_state()

    # Probabilities

    def get_probabilities(self):

        state = self.get_state()

        probabilities = state.probabilities_dict()

        return probabilities

    # Used by rebuild_circuit()

    def apply_gate(self, gate, qubit=0):

        gate = gate.upper()

        if gate == "H":
            self.h(qubit)

        elif gate == "X":
            self.x(qubit)

        elif gate == "Y":
            self.y(qubit)

        elif gate == "Z":
            self.z(qubit)

        elif gate == "S":
            self.s(qubit)

        elif gate == "T":
            self.t(qubit)

        elif gate == "RX":
            self.rx(1.57, qubit)

        elif gate == "RY":
            self.ry(1.57, qubit)

        elif gate == "RZ":
            self.rz(1.57, qubit)

        elif gate in ["M", "MEASURE"]:
            self.circuit.measure(qubit, qubit)

    def rebuild_from_grid(self, circuit_grid):

        rows = len(circuit_grid)

        self.num_qubits = rows

        self.reset()

        cols = len(circuit_grid[0])

        for c in range(cols):

            for q in range(rows):

                cell = circuit_grid[q][c]

                if cell is None:
                    continue

                cell_type = cell["type"]

                if cell_type == "single":

                    self.apply_gate(
                        cell["gate"],
                        q,
                    )

                elif cell_type == "measure":

                    self.circuit.measure(
                        q,
                        q,
                    )

                elif cell_type == "control":

                    self.apply_control_gate(
                        cell["gate"],
                        cell["control"],
                        cell["target"],
                    )

    def apply_control_gate(self, gate, control, target):
        gate = gate.upper()

        if gate == "CX":
            self.cx(control, target)

        elif gate == "CZ":
            self.cz(control, target)

        elif gate == "SWAP":
            self.swap(control, target)

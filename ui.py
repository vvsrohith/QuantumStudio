import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGraphicsScene,
    QGraphicsView,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from simulator import QuantumSimulator
from drawer import CircuitDrawer
from histogram import HistogramCanvas
from statevector import StatevectorCanvas
from bloch import BlochCanvas
from probability import ProbabilityCanvas
from exporter import CircuitExporter
from importer import CircuitImporter


class QuantumStudio(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Quantum Studio")
        self.resize(1450, 900)

        self.exporter = CircuitExporter()
        self.importer = CircuitImporter()

        self.simulator = QuantumSimulator(2)

        self.create_menu()

        self.central = QWidget()
        self.setCentralWidget(self.central)

        self.main_layout = QVBoxLayout(
            self.central
        )

        self.top_layout = QHBoxLayout()

        self.main_layout.addLayout(
            self.top_layout
        )

        self.build_gate_panel()
        self.build_circuit_panel()
        self.build_info_panel()
        self.build_bottom_tabs()

        self.status = QStatusBar()

        self.setStatusBar(
            self.status
        )

        self.status.showMessage(
            "Quantum Studio Ready"
        )

        self.drawer = CircuitDrawer(
            self.scene
        )

        self.drawer.draw_wires(2)


    def create_menu(self):

        menu = self.menuBar()

        file_menu = menu.addMenu("File")
        algorithm_menu = menu.addMenu("Algorithms")
        visualization_menu = menu.addMenu("Visualization")
        help_menu = menu.addMenu("Help")


        self.new_action = QAction(
            "New Circuit",
            self
        )

        self.open_action = QAction(
            "Open",
            self
        )

        self.save_action = QAction(
            "Save",
            self
        )

        self.export_png_action = QAction(
            "Export PNG",
            self
        )

        self.export_qasm_action = QAction(
            "Export QASM",
            self
        )

        self.exit_action = QAction(
            "Exit",
            self
        )


        file_menu.addAction(
            self.new_action
        )

        file_menu.addAction(
            self.open_action
        )

        file_menu.addAction(
            self.save_action
        )

        file_menu.addSeparator()

        file_menu.addAction(
            self.export_png_action
        )

        file_menu.addAction(
            self.export_qasm_action
        )

        file_menu.addSeparator()

        file_menu.addAction(
            self.exit_action
        )


        self.exit_action.triggered.connect(
            self.close
        )


        algorithm_menu.addAction(
            "Bell State"
        )

        algorithm_menu.addAction(
            "GHZ State"
        )

        algorithm_menu.addAction(
            "Quantum Teleportation"
        )

        algorithm_menu.addAction(
            "Grover Search"
        )

        algorithm_menu.addAction(
            "Deutsch"
        )

        algorithm_menu.addAction(
            "Quantum Fourier Transform"
        )


        visualization_menu.addAction(
            "Histogram"
        )

        visualization_menu.addAction(
            "Statevector"
        )

        visualization_menu.addAction(
            "Bloch Sphere"
        )


        help_menu.addAction(
            "About"
        )


    def build_gate_panel(self):

        gate_box = QGroupBox(
            "Quantum Gates"
        )

        layout = QGridLayout()


        gates = [
            "H",
            "X",
            "Y",
            "Z",
            "S",
            "T",
            "RX",
            "RY",
            "RZ",
            "CX",
            "CZ",
            "SWAP",
            "Measure",
            "Reset"
        ]


        row = 0
        col = 0


        for gate in gates:

            button = QPushButton(
                gate
            )

            button.setMinimumHeight(
                40
            )

            button.clicked.connect(
                lambda _, g=gate:
                self.add_gate(g)
            )


            layout.addWidget(
                button,
                row,
                col
            )


            col += 1


            if col == 2:

                row += 1
                col = 0


        gate_box.setLayout(
            layout
        )


        self.top_layout.addWidget(
            gate_box,
            1
        )


    def build_circuit_panel(self):

        circuit_box = QGroupBox(
            "Circuit Editor"
        )

        layout = QVBoxLayout()


        self.scene = QGraphicsScene()


        self.view = QGraphicsView(
            self.scene
        )


        layout.addWidget(
            self.view
        )


        circuit_box.setLayout(
            layout
        )


        self.top_layout.addWidget(
            circuit_box,
            4
        )


    def build_info_panel(self):

        info_box = QGroupBox(
            "Circuit Information"
        )

        layout = QVBoxLayout()


        layout.addWidget(
            QLabel("Number of Qubits")
        )


        self.qubits = QComboBox()


        self.qubits.addItems(
            [
                "1",
                "2",
                "3",
                "4",
                "5"
            ]
        )


        self.qubits.setCurrentText(
            "2"
        )


        self.qubits.currentIndexChanged.connect(
            self.on_qubits_changed
        )


        layout.addWidget(
            self.qubits
        )


        layout.addWidget(
            QLabel("Gate History")
        )


        self.history = QListWidget()


        layout.addWidget(
            self.history
        )


        self.run_button = QPushButton(
            "Run Circuit"
        )


        self.run_button.clicked.connect(
            self.run_circuit
        )


        layout.addWidget(
            self.run_button
        )


        info_box.setLayout(
            layout
        )


        self.top_layout.addWidget(
            info_box,
            1
        )


    def build_bottom_tabs(self):

        self.tabs = QTabWidget()


        self.circuit_tab = QTextEdit()

        self.circuit_tab.setReadOnly(
            True
        )


        self.histogram_tab = HistogramCanvas()

        self.statevector_tab = StatevectorCanvas()

        self.bloch_tab = BlochCanvas()


        self.probability_tab = ProbabilityCanvas()


        self.console_tab = QTextEdit()

        self.console_tab.setReadOnly(
            True
        )


        self.tabs.addTab(
            self.circuit_tab,
            "Circuit"
        )


        self.tabs.addTab(
            self.histogram_tab,
            "Histogram"
        )


        self.tabs.addTab(
            self.statevector_tab,
            "Statevector"
        )


        self.tabs.addTab(
            self.probability_tab,
            "Probability"
        )


        self.tabs.addTab(
            self.bloch_tab,
            "Bloch Sphere"
        )


        self.tabs.addTab(
            self.console_tab,
            "Console"
        )


        self.main_layout.addWidget(
            self.tabs
        )


    def on_qubits_changed(self):

        qubits = int(
            self.qubits.currentText()
        )


        self.simulator = QuantumSimulator(
            qubits
        )


        self.drawer.reset()


        self.drawer.draw_wires(
            qubits
        )


        self.history.clear()


        self.circuit_tab.clear()

        self.console_tab.clear()


        self.status.showMessage(
            f"{qubits} qubits selected"
        )


    def add_gate(self, gate):

        qubit = 0


        try:

            if gate == "H":

                self.simulator.h(
                    qubit
                )


            elif gate == "X":

                self.simulator.x(
                    qubit
                )


            elif gate == "Y":

                self.simulator.y(
                    qubit
                )


            elif gate == "Z":

                self.simulator.z(
                    qubit
                )


            elif gate == "S":

                self.simulator.s(
                    qubit
                )


            elif gate == "T":

                self.simulator.t(
                    qubit
                )


            elif gate == "RX":

                self.simulator.rx(
                    1.57,
                    qubit
                )


            elif gate == "RY":

                self.simulator.ry(
                    1.57,
                    qubit
                )


            elif gate == "RZ":

                self.simulator.rz(
                    1.57,
                    qubit
                )

            elif gate == "CX":

                self.simulator.cx(0, 1)
                self.drawer.add_control_gate("CX", 0, 1)

                self.history.addItem(gate)
                self.circuit_tab.append(gate)
                self.console_tab.append(f"Applied {gate}")
                self.status.showMessage(f"{gate} gate added")
                return

            elif gate == "CZ":

                self.simulator.cz(0, 1)
                self.drawer.add_control_gate("CZ", 0, 1)

                self.history.addItem(gate)
                self.circuit_tab.append(gate)
                self.console_tab.append(f"Applied {gate}")
                self.status.showMessage(f"{gate} gate added")
                return

            elif gate == "SWAP":

                self.simulator.swap(0, 1)
                self.drawer.add_control_gate("SWAP", 0, 1)

                self.history.addItem(gate)
                self.circuit_tab.append(gate)
                self.console_tab.append(f"Applied {gate}")
                self.status.showMessage(f"{gate} gate added")
                return
            
            elif gate == "Measure":
                self.simulator.measure_all()

            elif gate == "Reset":

                self.simulator.reset()


            self.drawer.add_gate(
                gate,
                qubit
            )


            self.history.addItem(
                gate
            )


            self.circuit_tab.append(
                gate
            )


            self.console_tab.append(
                f"Applied {gate}"
            )


            self.status.showMessage(
                f"{gate} gate added"
            )


        except Exception as e:

            self.console_tab.append(
                str(e)
            )


    def run_circuit(self):

        try:

            result = self.simulator.run()


            self.console_tab.append(
                "Circuit executed"
            )


            self.console_tab.append(
                str(result)
            )


            if hasattr(
                self.simulator,
                "get_counts"
            ):

                counts = (
                    self.simulator.get_counts()
                )


                self.histogram_tab.update_plot(
                    counts
                )


            if hasattr(
                self.simulator,
                "statevector"
            ):

                state = self.simulator.statevector()

                self.statevector_tab.update_state(state)

            try:
                    self.bloch_tab.update_state(state)

            except Exception as e:
                    self.console_tab.append(str(e))

            probs = self.simulator.get_probabilities()
            self.console_tab.append(str(probs))
            print("Updating probability tab...")
            self.probability_tab.update_probabilities(probs)


            self.status.showMessage(
                "Simulation Complete"
            )


        except Exception as e:

            self.console_tab.append(
                str(e)
            )


    def new_circuit(self):

        qubits = int(
            self.qubits.currentText()
        )

        self.simulator = QuantumSimulator(
            qubits
        )

        self.drawer.reset()

        self.drawer.draw_wires(
            qubits
        )

        self.history.clear()

        self.circuit_tab.clear()

        self.console_tab.clear()

        self.status.showMessage(
            "New circuit created"
        )


    def save_circuit(self):

        try:

            self.exporter.save(
                self.simulator.circuit
            )

            self.status.showMessage(
                "Circuit saved"
            )

        except Exception as e:

            self.console_tab.append(
                str(e)
            )


    def open_circuit(self):

        try:

            circuit = self.importer.load()

            if circuit:

                self.simulator.circuit = circuit

                self.circuit_tab.setText(
                    str(circuit)
                )

                self.console_tab.append(
                    "Circuit loaded"
                )


        except Exception as e:

            self.console_tab.append(
                str(e)
            )


    def export_png(self):

        try:

            self.exporter.export_png(
                self.simulator.circuit
            )

            self.status.showMessage(
                "PNG exported"
            )


        except Exception as e:

            self.console_tab.append(
                str(e)
            )


    def export_qasm(self):

        try:

            self.exporter.export_qasm(
                self.simulator.circuit
            )

            self.status.showMessage(
                "QASM exported"
            )


        except Exception as e:

            self.console_tab.append(
                str(e)
            )


    def about(self):

        self.console_tab.append(
            "Quantum Studio\n"
            "Quantum Circuit Designer\n"
            "Built using PySide6 and Qiskit"
        )


if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )


    window = QuantumStudio()

    window.show()


    sys.exit(
        app.exec()
    )
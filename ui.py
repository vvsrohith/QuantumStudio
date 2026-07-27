import copy
import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QKeySequence, QShortcut
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

# Custom module imports as required by the blueprint
from bloch import BlochCanvas
from drawer import CircuitDrawer
from exporter import CircuitExporter
from histogram import HistogramCanvas
from importer import CircuitImporter
from probability import ProbabilityCanvas
from simulator import QuantumSimulator
from statevector import StatevectorCanvas


class QuantumStudio(QMainWindow):

    def __init__(self):
        super().__init__()

        self.simulator = QuantumSimulator(2)

        self.undo_stack = []
        self.redo_stack = []
        self.clipboard = None

        self.animation_index = 0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_circuit)

        self.setWindowTitle("Quantum Studio")
        self.resize(1450, 900)

        self.exporter = CircuitExporter()
        self.importer = CircuitImporter()

        self.create_menu()

        self.central = QWidget()
        self.setCentralWidget(self.central)

        self.main_layout = QVBoxLayout(self.central)
        self.top_layout = QHBoxLayout()
        self.main_layout.addLayout(self.top_layout)

        self.build_gate_panel()
        self.build_circuit_panel()
        self.build_info_panel()
        self.build_bottom_tabs()

        self.setup_shortcuts()

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Quantum Studio Ready")

        self.drawer = CircuitDrawer(self.scene)
        self.drawer.selected_qubit = 0
        self.drawer.selected_column = 0
        self.drawer.redraw()

        self.view.setMouseTracking(True)
        self.view.mousePressEvent = self.circuit_clicked

    def setup_shortcuts(self):
        QShortcut(
            QKeySequence(Qt.Key_Delete),
            self,
            self.delete_selected_gate,
        )

        QShortcut(
            QKeySequence("Ctrl+C"),
            self,
            self.copy_gate,
        )

        QShortcut(
            QKeySequence("Ctrl+V"),
            self,
            self.paste_gate,
        )

    def create_menu(self):
        menu = self.menuBar()

        file_menu = menu.addMenu("File")
        algorithm_menu = menu.addMenu("Algorithms")
        visualization_menu = menu.addMenu("Visualization")
        help_menu = menu.addMenu("Help")

        self.new_action = QAction("New Circuit", self)
        self.open_action = QAction("Open", self)
        self.save_action = QAction("Save", self)
        self.export_png_action = QAction("Export PNG", self)
        self.export_qasm_action = QAction("Export QASM", self)
        self.exit_action = QAction("Exit", self)

        self.new_action.triggered.connect(self.new_circuit)
        self.open_action.triggered.connect(self.open_circuit)
        self.save_action.triggered.connect(self.save_circuit)
        self.export_png_action.triggered.connect(self.export_png)
        self.export_qasm_action.triggered.connect(self.export_qasm)
        self.exit_action.triggered.connect(self.close)

        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)

        file_menu.addSeparator()

        file_menu.addAction(self.export_png_action)
        file_menu.addAction(self.export_qasm_action)

        file_menu.addSeparator()

        file_menu.addAction(self.exit_action)

        algorithm_menu.addAction("Bell State")
        algorithm_menu.addAction("GHZ State")
        algorithm_menu.addAction("Quantum Teleportation")
        algorithm_menu.addAction("Grover Search")
        algorithm_menu.addAction("Deutsch")
        algorithm_menu.addAction("Quantum Fourier Transform")

        visualization_menu.addAction("Histogram")
        visualization_menu.addAction("Statevector")
        visualization_menu.addAction("Bloch Sphere")

        self.about_action = QAction("About", self)
        self.about_action.triggered.connect(self.about)

        help_menu.addAction(self.about_action)

    def build_gate_panel(self):
        gate_box = QGroupBox("Quantum Gates")

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
            "Reset",
        ]

        row = 0
        col = 0

        for gate in gates:
            button = QPushButton(gate)
            button.setMinimumHeight(40)
            button.clicked.connect(lambda _, g=gate: self.add_gate(g))

            layout.addWidget(
                button,
                row,
                col,
            )

            col += 1

            if col == 2:
                row += 1
                col = 0

        gate_box.setLayout(layout)

        self.top_layout.addWidget(
            gate_box,
            1,
        )

    def build_circuit_panel(self):
        circuit_box = QGroupBox("Circuit Editor")

        layout = QVBoxLayout()

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)

        layout.addWidget(self.view)

        circuit_box.setLayout(layout)

        self.top_layout.addWidget(
            circuit_box,
            4,
        )

    def build_info_panel(self):
        info_box = QGroupBox("Circuit Information")

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Number of Qubits"))

        self.qubits = QComboBox()
        self.qubits.addItems(["1", "2", "3", "4", "5"])
        self.qubits.setCurrentText("2")
        self.qubits.currentIndexChanged.connect(self.on_qubits_changed)

        layout.addWidget(self.qubits)

        layout.addWidget(QLabel("Gate History"))

        self.history = QListWidget()
        layout.addWidget(self.history)

        self.undo_button = QPushButton("Undo")
        self.undo_button.clicked.connect(self.undo_gate)
        layout.addWidget(self.undo_button)

        self.redo_button = QPushButton("Redo")
        self.redo_button.clicked.connect(self.redo_gate)
        layout.addWidget(self.redo_button)

        self.run_button = QPushButton("Run Circuit")
        self.run_button.clicked.connect(self.run_circuit)
        layout.addWidget(self.run_button)

        info_box.setLayout(layout)

        self.top_layout.addWidget(
            info_box,
            1,
        )

    def build_bottom_tabs(self):
        self.tabs = QTabWidget()

        self.circuit_tab = QTextEdit()
        self.circuit_tab.setReadOnly(True)

        self.histogram_tab = HistogramCanvas()
        self.statevector_tab = StatevectorCanvas()
        self.bloch_tab = BlochCanvas()
        self.probability_tab = ProbabilityCanvas()

        self.console_tab = QTextEdit()
        self.console_tab.setReadOnly(True)

        self.tabs.addTab(
            self.circuit_tab,
            "Circuit",
        )
        self.tabs.addTab(
            self.histogram_tab,
            "Histogram",
        )
        self.tabs.addTab(
            self.statevector_tab,
            "Statevector",
        )
        self.tabs.addTab(
            self.probability_tab,
            "Probability",
        )
        self.tabs.addTab(
            self.bloch_tab,
            "Bloch Sphere",
        )
        self.tabs.addTab(
            self.console_tab,
            "Console",
        )

        self.main_layout.addWidget(self.tabs)

    def build_simulator(self):
        self.simulator.reset()
        self.simulator.rebuild_from_grid(self.drawer.circuit_grid)

    def refresh_views(self):
        counts = self.simulator.get_counts()
        self.histogram_tab.update_plot(counts)

        try:
            state = self.simulator.get_state()
            self.statevector_tab.update_state(state)
            self.bloch_tab.update_state(state)
        except Exception as e:
            self.console_tab.append(str(e))

        probabilities = self.simulator.get_probabilities()
        self.probability_tab.update_probabilities(probabilities)

    def on_qubits_changed(self):
        qubits = int(self.qubits.currentText())

        self.simulator = QuantumSimulator(qubits)

        self.drawer.create_grid(qubits)
        self.drawer.selected_qubit = 0
        self.drawer.selected_column = 0

        self.clipboard = None

        self.drawer.redraw()

        self.undo_stack.clear()
        self.redo_stack.clear()

        self.history.clear()
        self.circuit_tab.clear()
        self.console_tab.clear()

        self.status.showMessage(f"{qubits} qubits selected")

    def add_gate(self, gate):
        self.undo_stack.append(copy.deepcopy(self.drawer.circuit_grid))
        self.redo_stack.clear()

        row = self.drawer.selected_qubit
        col = self.drawer.selected_column

        if gate in ["CX", "CZ", "SWAP"]:
            if self.drawer.qubits < 2:
                self.console_tab.append("Need at least 2 qubits.")
                return

            target = row + 1

            if target >= self.drawer.qubits:
                self.console_tab.append("No valid target qubit.")
                return

            self.drawer.add_control_gate(
                gate,
                row,
                target,
                col,
            )

        elif gate == "Measure":
            self.drawer.add_measure(
                row,
                col,
            )

        elif gate == "Reset":
            self.drawer.place_gate(
                "Reset",
                row,
                col,
            )

        else:
            self.drawer.place_gate(
                gate,
                row,
                col,
            )

        self.drawer.redraw()

        self.history.addItem(f"{gate} ({row},{col})")
        self.circuit_tab.append(f"{gate} -> q{row}, c{col}")
        self.console_tab.append(f"Added {gate}")
        self.status.showMessage(f"{gate} added")

    def run_circuit(self):
        try:
            self.build_simulator()
            self.animation_index = 0
            self.animation_timer.start(700)
        except Exception as e:
            self.console_tab.append(str(e))

    def animate_circuit(self):
        if not self.drawer.circuit_grid:
            return

        num_cols = len(self.drawer.circuit_grid[0])

        if self.animation_index < num_cols:
            for row in range(self.drawer.qubits):
                if self.drawer.circuit_grid[row][self.animation_index]:
                    self.drawer.highlight_cell(
                        row,
                        self.animation_index,
                    )

            self.animation_index += 1

        else:
            self.animation_timer.stop()
            self.simulator.run()
            self.refresh_views()

            self.status.showMessage("Simulation Complete")
            self.console_tab.append("Simulation Complete")

    def undo_gate(self):
        if self.undo_stack:
            self.redo_stack.append(copy.deepcopy(self.drawer.circuit_grid))
            self.drawer.circuit_grid = self.undo_stack.pop()
            self.drawer.redraw()
            self.status.showMessage("Undo")

    def redo_gate(self):
        if self.redo_stack:
            self.undo_stack.append(copy.deepcopy(self.drawer.circuit_grid))
            self.drawer.circuit_grid = self.redo_stack.pop()
            self.drawer.redraw()
            self.status.showMessage("Redo")

    def new_circuit(self):
        qubits = int(self.qubits.currentText())

        self.simulator = QuantumSimulator(qubits)

        self.drawer.create_grid(qubits)
        self.drawer.selected_qubit = 0
        self.drawer.selected_column = 0

        self.clipboard = None

        self.drawer.redraw()

        self.undo_stack.clear()
        self.redo_stack.clear()

        self.history.clear()
        self.circuit_tab.clear()
        self.console_tab.clear()

        self.status.showMessage("New circuit created")

    def save_circuit(self):
        try:
            self.build_simulator()
            self.exporter.save(self.simulator.circuit)
            self.status.showMessage("Circuit saved")
        except Exception as e:
            self.console_tab.append(str(e))

    def open_circuit(self):
        try:
            circuit = self.importer.load()

            if circuit:
                self.drawer.convert_circuit_to_grid(circuit)
                self.drawer.redraw()
                self.build_simulator()

                self.circuit_tab.setText(str(circuit))
                self.console_tab.append("Circuit loaded")

        except Exception as e:
            self.console_tab.append(str(e))

    def export_png(self):
        try:
            self.build_simulator()
            self.exporter.export_png(self.simulator.circuit)
            self.status.showMessage("PNG exported")
        except Exception as e:
            self.console_tab.append(str(e))

    def export_qasm(self):
        try:
            self.build_simulator()
            self.exporter.export_qasm(self.simulator.circuit)
            self.status.showMessage("QASM exported")
        except Exception as e:
            self.console_tab.append(str(e))

    def about(self):
        self.console_tab.append(
            "Quantum Studio\n"
            "Quantum Circuit Designer\n"
            "Built using PySide6 and Qiskit"
        )

    def select_cell(self, row, col):
        self.drawer.selected_qubit = row
        self.drawer.selected_column = col
        self.drawer.highlight_selected(row, col)

    def circuit_clicked(self, event):
        scene = self.view.mapToScene(event.pos())

        row, col = self.drawer.scene_to_grid(
            scene.x(),
            scene.y(),
        )

        if 0 <= row < self.drawer.qubits and 0 <= col < self.drawer.columns:
            self.select_cell(
                row,
                col,
            )

    def delete_selected_gate(self):
        row = self.drawer.selected_qubit
        col = self.drawer.selected_column

        self.undo_stack.append(copy.deepcopy(self.drawer.circuit_grid))
        self.redo_stack.clear()

        self.drawer.remove_gate(
            row,
            col,
        )

        self.drawer.redraw()

        self.history.addItem(f"Deleted ({row},{col})")
        self.console_tab.append("Gate deleted")
        self.status.showMessage("Gate deleted")

    def copy_gate(self):
        row = self.drawer.selected_qubit
        col = self.drawer.selected_column

        gate = self.drawer.circuit_grid[row][col]

        if gate is None:
            return

        self.clipboard = copy.deepcopy(gate)
        self.status.showMessage("Gate copied")

    def paste_gate(self):
        if self.clipboard is None:
            return

        row = self.drawer.selected_qubit
        col = self.drawer.selected_column

        self.undo_stack.append(copy.deepcopy(self.drawer.circuit_grid))
        self.redo_stack.clear()

        gate = self.clipboard["gate"]

        if gate in ["CX", "CZ", "SWAP"]:
            target = row + 1

            if target < self.drawer.qubits:
                self.drawer.add_control_gate(
                    gate,
                    row,
                    target,
                    col,
                )

        elif gate == "Measure":
            self.drawer.add_measure(
                row,
                col,
            )

        else:
            self.drawer.place_gate(
                gate,
                row,
                col,
            )

        self.drawer.redraw()

        self.history.addItem(f"Pasted {gate} ({row},{col})")
        self.console_tab.append(f"Pasted {gate}")
        self.status.showMessage(f"{gate} pasted")

    def move_gate(
        self,
        from_cell,
        to_cell,
    ):
        self.undo_stack.append(copy.deepcopy(self.drawer.circuit_grid))
        self.redo_stack.clear()

        self.drawer.move_gate(
            from_cell[0],
            from_cell[1],
            to_cell[0],
            to_cell[1],
        )

        self.drawer.redraw()
        self.status.showMessage("Gate moved")

    def replace_gate(
        self,
        row,
        col,
        gate,
    ):
        self.undo_stack.append(copy.deepcopy(self.drawer.circuit_grid))
        self.redo_stack.clear()

        self.drawer.replace_gate(
            row,
            col,
            gate,
        )

        self.drawer.redraw()
        self.status.showMessage("Gate replaced")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuantumStudio()
    window.show()
    sys.exit(app.exec())

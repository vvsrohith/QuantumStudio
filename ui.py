import os
import importlib
import copy
import json
import sys
import importlib
from pathlib import Path
from qiskit.qasm3 import dumps
from modules.workspace import Workspace
from modules.algorithm_runner import AlgorithmRunner
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from modules.algorithm_browser import AlgorithmBrowser
from modules.console_window import ConsoleWindow
from modules.statistics_window import StatisticsWindow
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGraphicsScene,
    QGraphicsView,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStatusBar,
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
from modules.project_manager import ProjectManager
from modules.settings_dialog import SettingsDialog


class QuantumStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        from PySide6.QtWidgets import QTextEdit

        self.console_tab = QTextEdit()
        self.console_window = ConsoleWindow()
        self.statistics_window = StatisticsWindow()
        self.console_tab.setReadOnly(True)
        self.circuit_console = QTextEdit()
        self.circuit_console.setReadOnly(True)

        self.settings = {
            "default_qubits": 2,
            "animation_speed": 700,
            "autosave": True,
        }

        self.load_settings()
        if "window_width" in self.settings:
            self.resize(
                self.settings["window_width"],
                self.settings["window_height"],
            )

        if "window_x" in self.settings:
            self.move(
                self.settings["window_x"],
                self.settings["window_y"],
            )

        self.simulator = QuantumSimulator(self.settings["default_qubits"])

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
        self.project_manager = ProjectManager()

        self.recent_files = []
        self.load_recent_files()

        self.central = QWidget()
        self.setCentralWidget(self.central)

        self.main_layout = QVBoxLayout(self.central)
        self.top_layout = QHBoxLayout()
        self.main_layout.addLayout(self.top_layout)

        self.build_gate_panel()
        self.build_circuit_panel()
        self.build_info_panel()
        self.workspace = Workspace()
        self.main_layout.addWidget(self.workspace)
        self.workspace.toolbar.view_requested.connect(self.open_plot_window)
        self.create_menu()

        self.detached_windows = {}
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Quantum Studio Ready")

        self.drawer = CircuitDrawer(self.scene, self)
        self.algorithm_runner = AlgorithmRunner(self)
        self.drawer.selected_qubit = 0
        self.drawer.selected_column = 0
        self.drawer.redraw()

        self.view.setMouseTracking(True)
        self.view.mousePressEvent = self.circuit_clicked
        self.restore_autosave()
        self.setup_shortcuts()
        if Path("autosave.json").exists():
            reply = QMessageBox.question(
                self,
                "Recover Session",
                "An autosaved circuit was found.\nRestore it?",
                QMessageBox.Yes | QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                self.load_autosave()

        if not Path("settings.json").exists():
            self.save_settings()

    def create_menu(self):

        menu = self.menuBar()

        file_menu = menu.addMenu("File")
        edit_menu = menu.addMenu("Edit")
        visualization_menu = menu.addMenu("Visualization")
        settings_menu = menu.addMenu("Settings")
        help_menu = menu.addMenu("Help")

        self.recent_projects_menu = file_menu.addMenu("Recent Projects")
        self.recent_menu = file_menu.addMenu("Recent Files")

        # -----------------------------
        # File
        # -----------------------------

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

        # -----------------------------
        # Edit
        # -----------------------------

        self.copy_action = QAction("Copy Gate", self)
        self.paste_action = QAction("Paste Gate", self)

        self.copy_action.triggered.connect(self.copy_gate)
        self.paste_action.triggered.connect(self.paste_gate)

        edit_menu.addAction(self.copy_action)
        edit_menu.addAction(self.paste_action)

        self.copy_shortcut = QShortcut(
            QKeySequence("Ctrl+C"),
            self,
        )
        self.copy_shortcut.activated.connect(self.copy_gate)

        self.paste_shortcut = QShortcut(
            QKeySequence("Ctrl+V"),
            self,
        )
        self.paste_shortcut.activated.connect(self.paste_gate)

        # -----------------------------
        # Algorithms
        # -----------------------------

        self.create_algorithm_menu()

        # -----------------------------
        # Visualization
        # -----------------------------

        circuit_action = QAction("Circuit", self)
        circuit_action.triggered.connect(self.show_circuit)

        console_action = QAction("Console", self)
        console_action.triggered.connect(self.show_console)

        statistics_action = QAction("Statistics", self)
        statistics_action.triggered.connect(self.show_statistics)

        hist_action = QAction("Histogram", self)
        hist_action.triggered.connect(lambda: self.open_plot_window("Histogram"))

        state_action = QAction("Statevector", self)
        state_action.triggered.connect(lambda: self.open_plot_window("Statevector"))

        bloch_action = QAction("Bloch Sphere", self)
        bloch_action.triggered.connect(lambda: self.open_plot_window("Bloch Sphere"))

        prob_action = QAction("Probability", self)
        prob_action.triggered.connect(lambda: self.open_plot_window("Probability"))

        visualization_menu.addAction(circuit_action)
        visualization_menu.addAction(console_action)
        visualization_menu.addAction(statistics_action)
        visualization_menu.addSeparator()
        visualization_menu.addAction(hist_action)
        visualization_menu.addAction(state_action)
        visualization_menu.addAction(prob_action)
        visualization_menu.addAction(bloch_action)

        # -----------------------------
        # Settings
        # -----------------------------

        self.preferences_action = QAction(
            "Preferences",
            self,
        )

        self.preferences_action.triggered.connect(self.open_settings)

        settings_menu.addAction(self.preferences_action)

        # -----------------------------
        # Help
        # -----------------------------

        self.about_action = QAction(
            "About",
            self,
        )

        self.about_action.triggered.connect(self.about)

        help_menu.addAction(self.about_action)

        self.update_recent_projects_menu()

    def show_circuit(self):
        self.workspace.show()
        self.workspace.raise_()

    def show_console(self):
        self.console_window.show()

    def show_statistics(self):
        stats = f"""
Quantum Circuit Statistics

Qubits:
{self.simulator.num_qubits}

Depth:
{self.simulator.circuit.depth()}

Gates:
{len(self.simulator.circuit.data)}
"""
        self.statistics_window.update_stats(stats)
        self.statistics_window.show()

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
        self.qubits.setCurrentText(str(self.settings["default_qubits"]))
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

        # ---------------------------------
        # Algorithm Information
        # ---------------------------------

        algorithm_box = QGroupBox("Algorithm")
        algorithm_box.setMinimumHeight(200)

        algorithm_layout = QVBoxLayout()

        self.algorithm_name = QLabel("No algorithm loaded")
        self.algorithm_name.setStyleSheet("font-weight:bold;font-size:15px;")

        self.algorithm_description = QLabel("")
        self.algorithm_description.setWordWrap(True)
        self.algorithm_description.setMinimumHeight(60)

        self.algorithm_qubits = QLabel("Qubits: -")
        self.algorithm_depth = QLabel("Depth: -")
        self.algorithm_gates = QLabel("Gate Count: -")

        algorithm_layout.addWidget(self.algorithm_name)
        algorithm_layout.addWidget(self.algorithm_description)
        algorithm_layout.addWidget(self.algorithm_qubits)
        algorithm_layout.addWidget(self.algorithm_depth)
        algorithm_layout.addWidget(self.algorithm_gates)

        algorithm_box.setLayout(algorithm_layout)

        layout.addWidget(algorithm_box)

        # ---------------------------------
        # Circuit Statistics
        # ---------------------------------

        stats_box = QGroupBox("Circuit Statistics")

        stats_layout = QVBoxLayout()

        self.stats_qubits = QLabel("Qubits: 0")
        self.stats_depth = QLabel("Depth: 0")
        self.stats_gates = QLabel("Gate Count: 0")
        self.stats_single = QLabel("Single-Qubit Gates: 0")
        self.stats_multi = QLabel("Multi-Qubit Gates: 0")
        self.stats_measurements = QLabel("Measurements: 0")

        stats_layout.addWidget(self.stats_qubits)
        stats_layout.addWidget(self.stats_depth)
        stats_layout.addWidget(self.stats_gates)
        stats_layout.addWidget(self.stats_single)
        stats_layout.addWidget(self.stats_multi)
        stats_layout.addWidget(self.stats_measurements)

        stats_box.setLayout(stats_layout)

        layout.addWidget(stats_box)

        info_box.setLayout(layout)

        self.top_layout.addWidget(
            info_box,
            1,
        )

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)

    def build_simulator(self):
        print("===== BUILDING SIMULATOR =====")
        print(self.drawer.circuit_grid)

        try:
            self.simulator.reset()
            self.simulator.rebuild_from_grid(self.drawer.circuit_grid)

            print("Circuit rebuilt successfully")
            print(self.simulator.circuit)

        except Exception as e:
            print("BUILD ERROR:", e)
            raise

        print("==============================")

    def update_simulation(self):
        try:
            self.build_simulator()

            self.simulator.run()
            self.refresh_views()

        except Exception as e:
            self.console_tab.append(str(e))

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
        self.circuit_console.clear()
        self.console_tab.clear()

        self.status.showMessage(f"{qubits} qubits selected")
        self.update_simulation()

    def get_state(self):

        if self.last_state:

            return self.last_state

        return Statevector(self.circuit.remove_final_measurements(inplace=False))

    def add_gate(self, gate):
        self.undo_stack.append(copy.deepcopy(self.drawer.circuit_grid))
        self.redo_stack.clear()

        row = self.drawer.selected_qubit
        col = self.drawer.selected_column

        angle = None

        if gate in ["RX", "RY", "RZ"]:
            angle, ok = QInputDialog.getText(
                self,
                "Rotation Gate",
                f"Enter angle for {gate}:",
                text="3.14159/2",
            )

            if not ok:
                return

        if gate in ["CX", "CZ", "SWAP"]:
            if self.drawer.qubits < 2:
                self.console_tab.append("Need at least 2 qubits.")
                return

            target = row + 1

            if target >= self.drawer.qubits:
                self.console_tab.append("No valid target qubit.")
                self.status.showMessage("Invalid target qubit")
                return

            if (
                self.drawer.circuit_grid[row][col] is not None
                or self.drawer.circuit_grid[target][col] is not None
            ):
                self.console_tab.append("Cell occupied")
                self.status.showMessage("Cell occupied")
                return

            self.drawer.add_control_gate(gate, row, target, col)

        elif gate == "Measure":
            if self.drawer.circuit_grid[row][col] is not None:
                self.console_tab.append("Cell occupied")
                return

            self.drawer.add_measure(row, col)

        else:
            if self.drawer.circuit_grid[row][col] is not None:
                self.replace_gate(row, col, gate)
                return

            self.drawer.place_gate(gate, row, col, angle)

        self.drawer.redraw()

        if angle is None:
            self.history.addItem(f"{gate} ({row},{col})")
            self.circuit_console.append(f"{gate} -> q{row}, c{col}")
            self.console_tab.append(f"Added {gate}")
        else:
            self.history.addItem(f"{gate}({angle}) ({row},{col})")
            self.circuit_console.append(f"{gate}({angle}) -> q{row}, c{col}")
            self.console_tab.append(f"Added {gate}({angle})")

        self.status.showMessage(f"{gate} added")

        if self.drawer.selected_column < self.drawer.columns - 1:
            self.drawer.selected_column += 1

        self.select_cell(
            self.drawer.selected_qubit,
            self.drawer.selected_column,
        )

        self.update_simulation()
        self.autosave_circuit()

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
            self.select_cell(
                self.drawer.selected_qubit,
                self.drawer.selected_column,
            )
            self.status.showMessage("Undo")
            self.update_simulation()
            self.autosave_circuit()

    def redo_gate(self):
        if self.redo_stack:
            self.undo_stack.append(copy.deepcopy(self.drawer.circuit_grid))
            self.drawer.circuit_grid = self.redo_stack.pop()
            self.drawer.redraw()
            self.select_cell(
                self.drawer.selected_qubit,
                self.drawer.selected_column,
            )
            self.status.showMessage("Redo")
            self.update_simulation()
            self.autosave_circuit()

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
        self.circuit_console.clear()
        self.console_tab.clear()

        self.status.showMessage("New circuit created")
        self.update_simulation()
        self.autosave_circuit()

    def save_circuit(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Circuit",
            "",
            "QuantumStudio Files (*.json)",
        )

        if not filename:
            return

        if not filename.endswith(".json"):
            filename += ".json"

        data = {
            "qubits": self.simulator.num_qubits,
            "grid": self.drawer.circuit_grid,
        }

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
                self.project_manager.add(filename)
                self.update_recent_projects_menu()
            self.add_recent_file(filename)
            self.console_tab.append(f"Saved circuit to {filename}")
            self.status.showMessage("Circuit saved")

        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

        self.autosave_circuit()

    def open_circuit(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Circuit",
            "",
            "QuantumStudio Files (*.json)",
        )

        if not filename:
            return

        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            qubits = data["qubits"]
            grid = data["grid"]

            self.qubits.setCurrentText(str(qubits))

            self.drawer.create_grid(qubits)
            self.drawer.circuit_grid = grid

            self.drawer.selected_qubit = 0
            self.drawer.selected_column = 0

            self.drawer.redraw()

            self.history.clear()
            self.circuit_console.clear()

            self.update_simulation()
            self.add_recent_file(filename)
            self.project_manager.add(filename)
            self.update_recent_projects_menu()
            self.console_tab.append(f"Loaded {Path(filename).name}")
            self.status.showMessage("Circuit loaded")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Open Error",
                str(e),
            )

    def load_autosave(self):
        try:
            with open("autosave.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            qubits = data["qubits"]
            grid = data["grid"]

            self.qubits.setCurrentText(str(qubits))

            self.drawer.create_grid(qubits)
            self.drawer.circuit_grid = grid

            self.drawer.selected_qubit = 0
            self.drawer.selected_column = 0

            self.drawer.redraw()

            self.history.clear()
            self.circuit_console.clear()

            self.update_simulation()

            self.console_tab.append("Autosave restored")
            self.status.showMessage("Recovered previous session")

        except Exception as e:
            QMessageBox.warning(
                self,
                "Recovery Error",
                str(e),
            )

    def export_png(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export PNG",
            "",
            "PNG Image (*.png)",
        )

        if not filename:
            return

        if not filename.endswith(".png"):
            filename += ".png"

        try:
            self.build_simulator()
            self.simulator.circuit.draw(
                output="mpl",
                filename=filename,
            )

            self.console_tab.append(f"PNG exported: {Path(filename).name}")
            self.status.showMessage("PNG exported")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def export_qasm(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export OpenQASM",
            "",
            "OpenQASM (*.qasm)",
        )

        if not filename:
            return

        if not filename.endswith(".qasm"):
            filename += ".qasm"

        try:
            self.build_simulator()

            qasm = dumps(self.simulator.circuit)

            with open(filename, "w", encoding="utf-8") as f:
                f.write(qasm)

            self.console_tab.append(f"QASM exported: {Path(filename).name}")
            self.status.showMessage("QASM exported")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def about(self):
        self.console_tab.append(
            "Quantum Studio\n"
            "Quantum Circuit Designer\n"
            "Built using PySide6 and Qiskit"
        )

    def open_preferences(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Preferences")

        layout = QFormLayout(dialog)

        qubits = QSpinBox()
        qubits.setRange(1, 5)
        qubits.setValue(self.settings["default_qubits"])

        speed = QSpinBox()
        speed.setRange(100, 2000)
        speed.setSingleStep(100)
        speed.setValue(self.settings["animation_speed"])

        autosave = QCheckBox()
        autosave.setChecked(self.settings["autosave"])

        layout.addRow("Default Qubits", qubits)
        layout.addRow("Animation Speed (ms)", speed)
        layout.addRow("Enable Autosave", autosave)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec():

            self.settings["default_qubits"] = qubits.value()
            self.settings["animation_speed"] = speed.value()
            self.settings["autosave"] = autosave.isChecked()

            self.save_settings()

            self.qubits.setCurrentText(str(self.settings["default_qubits"]))

        self.animation_timer.setInterval(self.settings["animation_speed"])

        self.console_tab.append("Preferences updated.")
        self.status.showMessage("Preferences saved")

    def select_cell(self, row, col):
        self.drawer.selected_qubit = row
        self.drawer.selected_column = col
        self.drawer.highlight_selected(row, col)
        self.statusBar().showMessage(f"Selected: Qubit {row} | Column {col}")

    def move_selection(self, row_change, col_change):

        row = self.drawer.selected_qubit + row_change
        col = self.drawer.selected_column + col_change

        row = max(0, min(row, self.drawer.qubits - 1))
        col = max(0, min(col, self.drawer.columns - 1))

        self.select_cell(
            row,
            col,
        )

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

        self.select_cell(
            self.drawer.selected_qubit,
            self.drawer.selected_column,
        )

        self.update_simulation()

        self.history.addItem(f"Deleted ({row},{col})")
        self.console_tab.append("Gate deleted")
        self.status.showMessage("Gate deleted")
        self.autosave_circuit()

    def copy_gate(self):
        row = self.drawer.selected_qubit
        col = self.drawer.selected_column

        gate = self.drawer.circuit_grid[row][col]

        if gate is None:
            self.status.showMessage("No gate selected")
            return

        self.clipboard = copy.deepcopy(gate)

        self.console_tab.append("Gate copied")
        self.status.showMessage("Gate copied")

    def paste_gate(self):
        if self.clipboard is None:
            self.status.showMessage("Clipboard is empty")
            return

        row = self.drawer.selected_qubit
        col = self.drawer.selected_column

        if self.drawer.circuit_grid[row][col] is not None:
            self.status.showMessage("Cell occupied")
            self.console_tab.append("Cannot paste: Cell occupied")
            return

        self.undo_stack.append(copy.deepcopy(self.drawer.circuit_grid))
        self.redo_stack.clear()

        gate = self.clipboard["gate"]

        if gate in ["RX", "RY", "RZ"]:
            angle = self.clipboard.get("angle", "3.14159/2")

            self.drawer.place_gate(
                gate,
                row,
                col,
                angle,
            )

        elif gate in ["CX", "CZ", "SWAP"]:
            target = row + 1

            if target >= self.drawer.qubits:
                self.status.showMessage("Invalid target qubit")
                return

            if self.drawer.circuit_grid[target][col] is not None:
                self.status.showMessage("Target cell occupied")
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

        self.history.addItem(f"Pasted {gate} ({row},{col})")
        self.circuit_console.append(f"{gate} -> q{row}, c{col}")
        self.console_tab.append(f"Pasted {gate}")
        self.status.showMessage(f"{gate} pasted")

        if self.drawer.selected_column < self.drawer.columns - 1:
            self.drawer.selected_column += 1

        self.select_cell(
            self.drawer.selected_qubit,
            self.drawer.selected_column,
        )

        self.update_simulation()
        self.autosave_circuit()

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

        existing = self.drawer.circuit_grid[row][col]
        if gate in ["RX", "RY", "RZ"]:

            current = existing.get("angle", "pi/2")

            angle, ok = QInputDialog.getText(
                self,
                "Edit Rotation",
                f"Angle for {gate}:",
                text=str(current),
            )

            if not ok:
                return

            existing["angle"] = angle

        if existing is None:
            return

        if existing["type"] == "measure":
            self.drawer.add_measure(row, col)

        elif existing["type"] == "control":
            self.console_tab.append("Cannot replace multi-qubit gate.")
            return

        elif existing["type"] == "target":
            self.console_tab.append("Select the control gate instead.")
            return

        else:
            self.drawer.place_gate(
                gate,
                row,
                col,
                existing.get("angle"),
            )

        self.drawer.redraw()

        self.select_cell(row, col)

        self.history.addItem(f"Replaced with {gate} ({row},{col})")

        self.console_tab.append(f"Replaced with {gate}")

        self.status.showMessage(f"{gate} replaced")

        self.update_simulation()
        self.autosave_circuit()

    def finish_algorithm_load(self, name):
        self.drawer.redraw()

        self.history.clear()
        self.history.addItem(f"Loaded {name}")

        self.circuit_console.clear()
        self.circuit_console.append(f"{name} Circuit Loaded")

        self.console_tab.append(f"{name} loaded")

        self.status.showMessage(f"{name} Ready")

        self.update_simulation()
        self.autosave_circuit()

    def autosave_circuit(self):
        data = {
            "qubits": int(self.qubits.currentText()),
            "grid": self.drawer.circuit_grid,
        }
        try:
            with open("autosave.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception:
            pass

    def add_recent_file(self, filename):
        print("Adding:", filename)
        print("Before:", self.recent_files)
        if filename in self.recent_files:
            self.recent_files.remove(filename)

        self.recent_files.insert(0, filename)

        self.recent_files = self.recent_files[:5]
        print("After:", self.recent_files)
        self.update_recent_menu()
        self.save_recent_files()

    def restore_autosave(self):

        if not os.path.exists("autosave.json"):
            return

        try:
            with open("autosave.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            qubits = data["qubits"]
            grid = data["grid"]

            self.qubits.setCurrentText(str(qubits))

            self.drawer.create_grid(qubits)
            self.drawer.circuit_grid = grid

            self.drawer.selected_qubit = 0
            self.drawer.selected_column = 0

            self.drawer.redraw()

            self.update_simulation()

            self.console_tab.append("Recovered autosaved session.")

        except Exception:
            pass

    def update_recent_menu(self):
        self.recent_menu.clear()

        if not self.recent_files:
            empty = QAction("(No Recent Files)", self)
            empty.setEnabled(False)
            self.recent_menu.addAction(empty)
            return

        for filename in self.recent_files:
            action = QAction(Path(filename).name, self)
            action.triggered.connect(lambda _, f=filename: self.open_recent_file(f))
            self.recent_menu.addAction(action)

    def open_recent_file(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)

            qubits = data["qubits"]
            grid = data["grid"]

            self.qubits.setCurrentText(str(qubits))
            self.drawer.create_grid(qubits)
            self.drawer.circuit_grid = grid

            self.drawer.selected_qubit = 0
            self.drawer.selected_column = 0

            self.drawer.redraw()
            self.history.clear()
            self.circuit_console.clear()

            self.update_simulation()

            self.status.showMessage("Circuit loaded")
            self.console_tab.append(f"Loaded {Path(filename).name}")

        except Exception as e:
            QMessageBox.warning(self, "Open Error", str(e))

    def save_recent_files(self):
        try:
            with open("recent_files.json", "w", encoding="utf-8") as f:
                json.dump(self.recent_files, f, indent=4)
        except Exception:
            pass

    def load_recent_files(self):
        try:
            if Path("recent_files.json").exists():
                with open("recent_files.json", "r", encoding="utf-8") as f:
                    self.recent_files = json.load(f)
            else:
                self.recent_files = []

        except Exception:
            self.recent_files = []

        if hasattr(self, "recent_menu"):
            self.update_recent_menu()

    def save_settings(self):
        try:
            self.settings["window_width"] = self.width()
            self.settings["window_height"] = self.height()
            self.settings["window_x"] = self.x()
            self.settings["window_y"] = self.y()
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            self.console_tab.append(f"Settings save error: {e}")

    def load_settings(self):
        try:
            if Path("settings.json").exists():
                with open("settings.json", "r", encoding="utf-8") as f:
                    self.settings = json.load(f)
            else:
                self.save_settings()
        except Exception as e:
            self.console_tab.append(f"Settings load error: {e}")

    def load_algorithm(self, module_name, display_name):
        print("LOAD ALGORITHM CALLED")
        try:
            module = importlib.import_module(f"algorithms.{module_name}")

            circuit = module.build()

            self.drawer.convert_circuit_to_grid(circuit)

            info = getattr(module, "INFO", {})
            print("Updating labels...")
            print(self.algorithm_name.text())
            self.algorithm_name.setText(info.get("name", display_name))

            self.algorithm_description.setText(info.get("description", ""))

            self.algorithm_qubits.setText(f"Qubits: {circuit.num_qubits}")

            self.algorithm_depth.setText(f"Depth: {circuit.depth()}")

            self.algorithm_gates.setText(f"Gate Count: {len(circuit.data)}")

            self.finish_algorithm_load(display_name)

        except Exception as e:
            self.console_tab.append(f"Error loading {display_name}: {e}")
            self.status.showMessage("Algorithm Load Failed")

    def create_algorithm_menu(self):

        algorithm_menu = self.menuBar().addMenu("Algorithms")

        folder = "algorithms"

        if not os.path.isdir(folder):
            return

        for filename in sorted(os.listdir(folder)):

            if filename.startswith("_") or not filename.endswith(".py"):
                continue

            module_name = filename[:-3]

            try:
                module = importlib.import_module(f"algorithms.{module_name}")

                if not hasattr(module, "build"):
                    continue

                display_name = getattr(
                    module,
                    "DISPLAY_NAME",
                    module_name.replace("_", " ").title(),
                )

                action = QAction(display_name, self)

                action.triggered.connect(
                    lambda checked=False, m=module_name, d=display_name: self.load_algorithm(
                        m, d
                    )
                )

                algorithm_menu.addAction(action)

            except Exception as e:
                if hasattr(self, "console_tab"):
                    self.console_tab.append(
                        f"Failed to load algorithm '{module_name}': {e}"
                    )
        algorithm_menu.addSeparator()
        browse = QAction("Browse Algorithms...", self)
        browse.triggered.connect(self.show_algorithm_browser)
        algorithm_menu.addAction(browse)

    def show_algorithm_browser(self):

        algorithms = {}

        folder = "algorithms"

        for filename in os.listdir(folder):

            if filename.endswith(".py") and filename != "__init__.py":

                display = filename[:-3].replace("_", " ").title()

                module = filename[:-3]

                algorithms[display] = module

        browser = AlgorithmBrowser(algorithms, self)

        if browser.exec():

            name = browser.selected_algorithm()

            if name:
                self.load_algorithm(
                    algorithms[name],
                    name,
                )

    def update_recent_projects_menu(self):

        self.recent_projects_menu.clear()

        projects = self.project_manager.recent()

        if not projects:

            action = QAction("No Recent Projects", self)
            action.setEnabled(False)
            self.recent_projects_menu.addAction(action)
            return

        for filename in projects:

            action = QAction(Path(filename).name, self)

            action.triggered.connect(
                lambda checked=False, f=filename: self.open_recent_project(f)
            )

            self.recent_projects_menu.addAction(action)

    def open_recent_project(self, filename):

        if not os.path.exists(filename):

            QMessageBox.warning(
                self,
                "File Missing",
                "Project file not found.",
            )

            self.update_recent_projects_menu()

            return

        try:

            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)

            qubits = data["qubits"]
            grid = data["grid"]

            self.qubits.setCurrentText(str(qubits))

            self.drawer.create_grid(qubits)
            self.drawer.circuit_grid = grid

            self.drawer.selected_qubit = 0
            self.drawer.selected_column = 0

            self.drawer.redraw()

            self.history.clear()
            self.circuit_console.clear()

            self.update_simulation()

            self.project_manager.add(filename)

            self.update_recent_projects_menu()

            self.console_tab.append(f"Loaded {Path(filename).name}")

            self.status.showMessage("Circuit loaded")

        except Exception as e:

            QMessageBox.critical(
                self,
                "Open Error",
                str(e),
            )

    def open_plot_window(self, view):

        from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit

        if not hasattr(self, "plot_windows"):
            self.plot_windows = {}

        if view in self.plot_windows:

            w = self.plot_windows[view]
            w.showNormal()
            w.raise_()
            w.activateWindow()

            if view == "Circuit":

                canvas = w.layout().itemAt(0).widget()
                canvas.clear()

                for row in range(self.drawer.qubits):

                    line = f"Q{row}: "

                    for col in range(self.drawer.columns):

                        cell = self.drawer.circuit_grid[row][col]

                        if cell is None:
                            line += "---- "

                        elif cell["type"] == "single":
                            line += f"{cell['gate']} "

                        elif cell["type"] == "control":
                            line += "● "

                        elif cell["type"] == "target":

                            if cell["gate"] == "CX":
                                line += "⊕ "

                            elif cell["gate"] == "CZ":
                                line += "Z "

                            elif cell["gate"] == "SWAP":
                                line += "× "

                            else:
                                line += f"{cell['gate']} "

                        elif cell["type"] == "measure":
                            line += "M "

                        else:
                            line += "? "

                    canvas.append(line)

            elif view == "Console":

                canvas = w.layout().itemAt(0).widget()
                canvas.setPlainText(self.console_tab.toPlainText())

            elif view == "Statistics":

                canvas = w.layout().itemAt(0).widget()
                canvas.setPlainText(f"""Qubits: {self.simulator.num_qubits}
    Depth: {self.simulator.circuit.depth()}
    Gate Count: {len(self.simulator.circuit.data)}""")

            return

        window = QWidget()
        window.setWindowTitle(view)
        window.resize(900, 650)

        layout = QVBoxLayout(window)

        if view == "Histogram":

            canvas = HistogramCanvas()

            try:
                canvas.update_plot(self.simulator.get_counts())
            except Exception:
                pass

        elif view == "Statevector":

            canvas = StatevectorCanvas()

            try:
                canvas.update_state(self.simulator.get_state())
            except Exception:
                pass

        elif view == "Bloch Sphere":

            canvas = BlochCanvas()

            try:
                canvas.update_state(self.simulator.get_state())
            except Exception:
                pass

        elif view == "Probability":

            canvas = ProbabilityCanvas()

            try:
                canvas.update_probabilities(self.simulator.get_probabilities())
            except Exception:
                pass

        elif view == "Circuit":

            canvas = QTextEdit()
            canvas.setReadOnly(True)

            for row in range(self.drawer.qubits):

                line = f"Q{row}: "

                for col in range(self.drawer.columns):

                    cell = self.drawer.circuit_grid[row][col]

                    if cell is None:
                        line += "---- "

                    elif cell["type"] == "single":
                        line += f"{cell['gate']} "

                    elif cell["type"] == "control":
                        line += "● "

                    elif cell["type"] == "target":

                        if cell["gate"] == "CX":
                            line += "⊕ "

                        elif cell["gate"] == "CZ":
                            line += "Z "

                        elif cell["gate"] == "SWAP":
                            line += "× "

                        else:
                            line += f"{cell['gate']} "

                    elif cell["type"] == "measure":
                        line += "M "

                    else:
                        line += "? "

                canvas.append(line)

        elif view == "Console":

            canvas = QTextEdit()
            canvas.setReadOnly(True)
            canvas.setPlainText(self.console_tab.toPlainText())

        elif view == "Statistics":

            canvas = QTextEdit()
            canvas.setReadOnly(True)
            canvas.setPlainText(f"""Qubits: {self.simulator.num_qubits}
    Depth: {self.simulator.circuit.depth()}
    Gate Count: {len(self.simulator.circuit.data)}""")

        else:
            return

        layout.addWidget(canvas)

        self.plot_windows[view] = window

        window.show()

    def setup_shortcuts(self):

        # Navigation
        QShortcut(
            QKeySequence(Qt.Key_Left),
            self,
            lambda: self.move_selection(0, -1),
        )

        QShortcut(
            QKeySequence(Qt.Key_Right),
            self,
            lambda: self.move_selection(0, 1),
        )

        QShortcut(
            QKeySequence(Qt.Key_Up),
            self,
            lambda: self.move_selection(-1, 0),
        )

        QShortcut(
            QKeySequence(Qt.Key_Down),
            self,
            lambda: self.move_selection(1, 0),
        )

        # Gate shortcuts
        QShortcut(
            QKeySequence("H"),
            self,
            lambda: self.add_gate("H"),
        )

        QShortcut(
            QKeySequence("X"),
            self,
            lambda: self.add_gate("X"),
        )

        QShortcut(
            QKeySequence("Y"),
            self,
            lambda: self.add_gate("Y"),
        )

        QShortcut(
            QKeySequence("Z"),
            self,
            lambda: self.add_gate("Z"),
        )

        QShortcut(
            QKeySequence("S"),
            self,
            lambda: self.add_gate("S"),
        )

        QShortcut(
            QKeySequence("T"),
            self,
            lambda: self.add_gate("T"),
        )

        QShortcut(
            QKeySequence("M"),
            self,
            lambda: self.add_gate("Measure"),
        )

        # File shortcuts
        QShortcut(
            QKeySequence("Ctrl+N"),
            self,
            activated=self.new_circuit,
        )

        QShortcut(
            QKeySequence("Ctrl+O"),
            self,
            activated=self.open_circuit,
        )

        QShortcut(
            QKeySequence("Ctrl+S"),
            self,
            activated=self.save_circuit,
        )

        # Edit shortcuts
        QShortcut(
            QKeySequence("Ctrl+Z"),
            self,
            activated=self.undo_gate,
        )

        QShortcut(
            QKeySequence("Ctrl+Y"),
            self,
            activated=self.redo_gate,
        )

        QShortcut(
            QKeySequence("Ctrl+Shift+Z"),
            self,
            activated=self.redo_gate,
        )

        QShortcut(
            QKeySequence("Delete"),
            self,
            activated=self.delete_selected_gate,
        )

    def refresh_views(self):

        try:
            counts = self.simulator.get_counts()
            state = self.simulator.get_state()
            probabilities = self.simulator.get_probabilities()

            if hasattr(self, "plot_windows"):

                if "Histogram" in self.plot_windows:

                    canvas = self.plot_windows["Histogram"].layout().itemAt(0).widget()

                    canvas.update_plot(counts)

                if "Statevector" in self.plot_windows:

                    canvas = (
                        self.plot_windows["Statevector"].layout().itemAt(0).widget()
                    )

                    canvas.update_state(state)

                if "Bloch Sphere" in self.plot_windows:

                    canvas = (
                        self.plot_windows["Bloch Sphere"].layout().itemAt(0).widget()
                    )

                    canvas.update_state(state)

                if "Probability" in self.plot_windows:

                    canvas = (
                        self.plot_windows["Probability"].layout().itemAt(0).widget()
                    )

                    canvas.update_probabilities(probabilities)

        except Exception as e:

            print("Refresh Views Error:", e)

    def open_settings(self):

        dialog = SettingsDialog(
            self.settings,
            self,
        )

        if dialog.exec():

            self.settings = dialog.get_settings()

            self.qubits.setCurrentText(str(self.settings["default_qubits"]))

            self.animation_timer.setInterval(self.settings["animation_speed"])

            self.save_settings()

            self.status.showMessage(
                "Settings Saved",
                3000,
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuantumStudio()
    window.show()
    sys.exit(app.exec())

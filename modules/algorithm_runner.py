import importlib.util
import os


class AlgorithmRunner:

    def __init__(self, ui):
        self.ui = ui

    def run_algorithm(self, filename):
        if not os.path.exists(filename):
            return

        spec = importlib.util.spec_from_file_location(
            "algorithm_module",
            filename,
        )

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, "build"):
            return

        circuit = module.build()

        info = getattr(module, "INFO", {})

        self.ui.algorithm_name.setText(info.get("name", os.path.basename(filename)))

        self.ui.algorithm_description.setText(info.get("description", ""))

        self.ui.algorithm_qubits.setText(f"Qubits: {circuit.num_qubits}")

        self.ui.algorithm_depth.setText(f"Depth: {circuit.depth()}")

        self.ui.algorithm_gates.setText(f"Gate Count: {len(circuit.data)}")

        self.ui.drawer.convert_circuit_to_grid(circuit)

        self.ui.build_simulator()

        self.ui.refresh_views()

        self.ui.statusBar().showMessage(
            f"Loaded {info.get('name', os.path.basename(filename))}",
            3000,
        )

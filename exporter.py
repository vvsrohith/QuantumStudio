from pathlib import Path

from qiskit import qasm2
from qiskit.visualization import circuit_drawer


class CircuitExporter:

    def __init__(self):

        self.export_folder = Path("exports")

        self.export_folder.mkdir(
            exist_ok=True
        )

    def export_png(
        self,
        circuit,
        filename="circuit.png"
    ):

        path = self.export_folder / filename

        circuit_drawer(
            circuit,
            output="mpl",
            filename=str(path)
        )

        return str(path)

    def export_qasm(
        self,
        circuit,
        filename="circuit.qasm"
    ):

        path = self.export_folder / filename

        qasm = qasm2.dumps(circuit)

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(qasm)

        return str(path)

    def export_text(
        self,
        circuit,
        filename="circuit.txt"
    ):

        path = self.export_folder / filename

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(str(circuit))

        return str(path)
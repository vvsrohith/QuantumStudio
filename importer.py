from pathlib import Path

from qiskit import qasm2


class CircuitImporter:

    def __init__(self):

        self.import_folder = Path("saved")

        self.import_folder.mkdir(
            exist_ok=True
        )

    def load_qasm(self, filename):

        path = self.import_folder / filename

        if not path.exists():
            raise FileNotFoundError(
                f"{filename} not found."
            )

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            qasm = file.read()

        return qasm2.loads(qasm)

    def list_saved(self):

        return sorted(
            [
                file.name
                for file in self.import_folder.glob("*.qasm")
            ]
        )

    def exists(self, filename):

        return (
            self.import_folder / filename
        ).exists()
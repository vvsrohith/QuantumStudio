from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtGui import (
    QBrush,
    QColor,
    QPen,
)
from PySide6.QtWidgets import (
    QGraphicsRectItem,
    QGraphicsSimpleTextItem,
)


class CircuitScene(QGraphicsScene):

    def __init__(self, drawer):
        super().__init__()
        self.drawer = drawer

    def mousePressEvent(self, event):
        pos = event.scenePos()

        qubit, column = self.drawer.scene_to_grid(pos.x(), pos.y())

        self.drawer.selected_qubit = qubit
        self.drawer.selected_column = column

        self.drawer.highlight_selected(qubit, column)

        if hasattr(self.drawer, "parent"):
            self.drawer.parent.select_cell(qubit, column)

        super().mousePressEvent(event)


class CircuitDrawer:

    def __init__(self, scene, parent=None):
        self.scene = scene
        self.parent = parent
        self.qubits = 2
        self.columns = 32
        self.current_column = 0
        self.selected_qubit = 0
        self.selected_column = 0
        self.drag_start = None
        self.x_start = 100
        self.y_start = 60

        self.x_spacing = 80
        self.y_spacing = 80

        self.circuit_grid = []
        self.gate_items = []
        self.selection_item = None
        self.highlight_item = None
        self.drag_start = None

        self.create_grid(self.qubits)

    # ----------------------------------------------------
    # Grid
    # ----------------------------------------------------

    def create_grid(self, qubits):
        self.qubits = qubits
        self.circuit_grid = [[None for _ in range(self.columns)] for _ in range(qubits)]
        self.current_column = 0
        self.selected_qubit = 0
        self.selected_column = 0

    def reset(self):
        self.scene.clear()
        self.gate_items = []
        self.selection_item = None
        self.highlight_item = None
        self.create_grid(self.qubits)

    # ----------------------------------------------------
    # Coordinates
    # ----------------------------------------------------

    def get_x(self, column):
        return self.x_start + column * self.x_spacing

    def get_y(self, qubit):
        return self.y_start + qubit * self.y_spacing

    def scene_to_grid(self, x, y):
        column = round((x - self.x_start) / self.x_spacing)
        qubit = round((y - self.y_start) / self.y_spacing)

        column = max(0, min(column, self.columns - 1))
        qubit = max(0, min(qubit, self.qubits - 1))

        return qubit, column

    # ----------------------------------------------------
    # Helpers
    # ----------------------------------------------------

    def find_next_column(self):
        for c in range(self.columns):
            empty = True
            for q in range(self.qubits):
                if self.circuit_grid[q][c] is not None:
                    empty = False
                    break
            if empty:
                return c
        return self.columns - 1

    # ----------------------------------------------------
    # Wire Drawing
    # ----------------------------------------------------

    def draw_wires(self, qubits=None):
        num_qubits = qubits if qubits is not None else self.qubits
        for q in range(num_qubits):
            y = self.get_y(q)
            self.scene.addLine(
                40,
                y,
                self.get_x(self.columns),
                y,
                QPen(QColor("black"), 2),
            )

    # ----------------------------------------------------
    # Single Gate Drawing
    # ----------------------------------------------------

    def draw_single_gate(
        self,
        gate,
        row,
        column,
        colour="#4da6ff",
        angle=None,
    ):
        x = self.get_x(column)
        y = self.get_y(row)

        rect = QGraphicsRectItem(x, y - 20, 40, 40)
        rect.setBrush(QBrush(QColor(colour)))
        self.scene.addItem(rect)

        text = QGraphicsSimpleTextItem(gate)
        text.setPos(x + 10, y - 18)
        self.scene.addItem(text)

        items = [rect, text]

        if angle is not None:
            angle_text = QGraphicsSimpleTextItem(str(angle))
            angle_text.setScale(0.6)
            angle_text.setPos(x + 4, y + 2)
            self.scene.addItem(angle_text)
            items.append(angle_text)

        self.gate_items.append(
            {
                "row": row,
                "column": column,
                "items": items,
            }
        )

    # ----------------------------------------------------
    # Control Gate Drawing
    # ----------------------------------------------------

    def draw_control_gate(self, gate, control, target, column):
        x = self.get_x(column)
        cy = self.get_y(control)
        ty = self.get_y(target)

        group = []

        dot = self.scene.addEllipse(
            x + 15,
            cy - 5,
            10,
            10,
            QPen(QColor("black")),
            QBrush(QColor("black")),
        )
        group.append(dot)

        line = self.scene.addLine(
            x + 20,
            cy,
            x + 20,
            ty,
            QPen(QColor("black"), 2),
        )
        group.append(line)

        if gate == "CX":
            circle = self.scene.addEllipse(x + 8, ty - 12, 24, 24)
            v = self.scene.addLine(x + 20, ty - 12, x + 20, ty + 12)
            h = self.scene.addLine(x + 8, ty, x + 32, ty)
            group.extend([circle, v, h])

        elif gate == "CZ":
            rect = QGraphicsRectItem(x, ty - 20, 40, 40)
            rect.setBrush(QBrush(QColor("#ffb347")))
            self.scene.addItem(rect)

            text = QGraphicsSimpleTextItem("Z")
            text.setPos(x + 12, ty - 12)
            self.scene.addItem(text)

            group.extend([rect, text])

        elif gate == "SWAP":
            s1 = self.scene.addLine(x + 10, cy - 10, x + 30, cy + 10)
            s2 = self.scene.addLine(x + 30, cy - 10, x + 10, cy + 10)
            s3 = self.scene.addLine(x + 10, ty - 10, x + 30, ty + 10)
            s4 = self.scene.addLine(x + 30, ty - 10, x + 10, ty + 10)
            group.extend([s1, s2, s3, s4])

        self.gate_items.append(
            {
                "row": control,
                "column": column,
                "items": group,
            }
        )

    # ----------------------------------------------------
    # Selection & Highlighting
    # ----------------------------------------------------

    def draw_selection(self):
        if self.selection_item:
            self.scene.removeItem(self.selection_item)

        x = self.get_x(self.selected_column)
        y = self.get_y(self.selected_qubit)

        self.selection_item = QGraphicsRectItem(x - 4, y - 24, 48, 48)
        pen = QPen(QColor("#ff0000"), 2)
        self.selection_item.setPen(pen)
        self.scene.addItem(self.selection_item)

    def highlight_selected(self, qubit, column):
        x = self.get_x(column)
        y = self.get_y(qubit)

        rect = self.scene.addRect(
            x - 4,
            y - 24,
            48,
            48,
            QPen(QColor("red"), 2),
        )
        rect.setZValue(100)

    def highlight_cell(self, qubit, column):
        x = self.get_x(column)
        y = self.get_y(qubit)

        rect = self.scene.addRect(
            x - 2,
            y - 22,
            44,
            44,
            QPen(QColor("green"), 2),
        )
        rect.setZValue(90)

    # ----------------------------------------------------
    # Redraw
    # ----------------------------------------------------

    def redraw(self):
        self.scene.clear()
        self.gate_items = []
        self.selection_item = None
        self.highlight_item = None

        self.draw_wires(self.qubits)

        for row in range(self.qubits):
            for col in range(self.columns):
                gate = self.circuit_grid[row][col]
                if gate is None:
                    continue

                gate_type = gate.get("type")

                if gate_type == "single":
                    self.draw_single_gate(
                        gate["gate"],
                        row,
                        col,
                        angle=gate.get("angle"),
                    )
                elif gate_type == "measure":
                    self.draw_single_gate(
                        "M",
                        row,
                        col,
                        "#7ed957",
                    )
                elif gate_type == "control":
                    if gate.get("control") != row:
                        continue
                    self.draw_control_gate(
                        gate["gate"],
                        gate["control"],
                        gate["target"],
                        col,
                    )

        self.current_column = self.find_next_column()
        self.highlight_selected(self.selected_qubit, self.selected_column)

    # ----------------------------------------------------
    # Gate Manipulation & Placement
    # ----------------------------------------------------

    def place_gate(self, gate, qubit, column, angle=None):
        self.circuit_grid[qubit][column] = {
            "type": "single",
            "gate": gate,
            "angle": angle,
        }
        self.current_column = self.find_next_column()

    def add_measure(self, qubit, column):
        self.circuit_grid[qubit][column] = {
            "type": "measure",
            "gate": "M",
        }
        self.current_column = self.find_next_column()

    def add_control_gate(self, gate, control, target, column):
        self.circuit_grid[control][column] = {
            "type": "control",
            "gate": gate,
            "control": control,
            "target": target,
        }
        self.circuit_grid[target][column] = {
            "type": "target",
            "gate": gate,
            "control": control,
            "target": target,
        }
        self.current_column = self.find_next_column()

    def remove_gate(self, qubit, column):
        self.circuit_grid[qubit][column] = None

    def replace_gate(self, qubit, column, gate):
        self.circuit_grid[qubit][column] = {
            "type": "single",
            "gate": gate,
        }

    def move_gate(self, from_row, from_col, to_row, to_col):
        gate = self.circuit_grid[from_row][from_col]
        if gate is None:
            return
        self.circuit_grid[to_row][to_col] = gate
        self.circuit_grid[from_row][from_col] = None

    # ----------------------------------------------------
    # Circuit Conversion
    # ----------------------------------------------------

    def convert_circuit_to_grid(self, circuit):
        self.create_grid(circuit.num_qubits)
        column = 0

        for instruction in circuit.data:
            operation = instruction.operation
            qubits = instruction.qubits
            name = operation.name.upper()

            if len(qubits) == 1:
                row = circuit.find_bit(qubits[0]).index
                self.place_gate(name, row, column)

            elif len(qubits) == 2:
                control = circuit.find_bit(qubits[0]).index
                target = circuit.find_bit(qubits[1]).index

                gate = "CX"
                if name == "CZ":
                    gate = "CZ"
                elif name == "SWAP":
                    gate = "SWAP"

                self.add_control_gate(gate, control, target, column)

            column += 1

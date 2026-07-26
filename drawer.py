from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsSimpleTextItem


class CircuitDrawer:

    def __init__(self, scene):
        self.scene = scene
        self.qubits = 2
        self.step = 0

    def reset(self):
        self.scene.clear()
        self.step = 0

    def draw_wires(self, qubits):

        self.qubits = qubits

        for i in range(qubits):
            y = 60 + i * 80
            self.scene.addLine(
                40,
                y,
                1200,
                y,
                QPen(QColor("black"), 2)
            )

    def add_gate(self, gate, qubit):

        x = 100 + self.step * 70
        y = 60 + qubit * 80

        rect = QGraphicsRectItem(
            x,
            y - 20,
            40,
            40
        )

        rect.setBrush(QBrush(QColor("#4da6ff")))

        self.scene.addItem(rect)

        text = QGraphicsSimpleTextItem(gate)
        text.setPos(x + 11, y - 12)

        self.scene.addItem(text)

        self.step += 1

    def add_control_gate(self, gate, control, target):

        x = 100 + self.step * 70

        cy = 60 + control * 80
        ty = 60 + target * 80

        self.scene.addEllipse(
            x + 15,
            cy - 5,
            10,
            10,
            QPen(QColor("black")),
            QBrush(QColor("black"))
        )

        self.scene.addLine(
            x + 20,
            cy,
            x + 20,
            ty,
            QPen(QColor("black"), 2)
        )

        if gate == "CX":

            self.scene.addEllipse(
                x + 8,
                ty - 12,
                24,
                24
            )

            self.scene.addLine(
                x + 20,
                ty - 12,
                x + 20,
                ty + 12
            )

            self.scene.addLine(
                x + 8,
                ty,
                x + 32,
                ty
            )

        elif gate == "CZ":

            rect = QGraphicsRectItem(
                x,
                ty - 20,
                40,
                40
            )

            rect.setBrush(QBrush(QColor("#ffb347")))

            self.scene.addItem(rect)

            text = QGraphicsSimpleTextItem("Z")
            text.setPos(x + 12, ty - 12)

            self.scene.addItem(text)

        elif gate == "SWAP":

            self.scene.addLine(x + 10, cy - 10, x + 30, cy + 10)
            self.scene.addLine(x + 30, cy - 10, x + 10, cy + 10)

            self.scene.addLine(x + 10, ty - 10, x + 30, ty + 10)
            self.scene.addLine(x + 30, ty - 10, x + 10, ty + 10)

            self.scene.addLine(
                x + 20,
                cy,
                x + 20,
                ty
            )

        self.step += 1
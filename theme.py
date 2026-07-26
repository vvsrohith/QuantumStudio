from PySide6.QtWidgets import QApplication


def apply_theme(app):

    app.setStyleSheet("""

    QMainWindow {
        background-color: #0b1220;
    }

    QWidget {
        background-color: #0b1220;
        color: #e6edf3;
        font-size: 14px;
    }


    QGroupBox {

        border: 1px solid #263238;
        border-radius: 10px;
        margin-top: 12px;
        padding: 12px;
        font-weight: bold;
        color: #64ffda;
    }


    QGroupBox::title {

        subcontrol-origin: margin;
        left: 15px;
        padding: 0 5px;
    }


    QPushButton {

        background-color: #172554;
        border-radius: 8px;
        padding: 8px;
        border: 1px solid #334155;
    }


    QPushButton:hover {

        background-color: #2563eb;
    }


    QPushButton:pressed {

        background-color: #1d4ed8;
    }


    QComboBox {

        background-color: #111827;
        border: 1px solid #374151;
        padding: 6px;
        border-radius: 6px;
    }


    QListWidget,
    QTextEdit {

        background-color: #020617;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 8px;
    }


    QTabWidget::pane {

        border: 1px solid #334155;
        border-radius: 8px;
    }


    QTabBar::tab {

        background-color: #111827;
        padding: 10px;
        border-radius: 6px;
        margin: 2px;
    }


    QTabBar::tab:selected {

        background-color: #2563eb;
        color: white;
    }


    QMenuBar {

        background-color: #020617;
    }


    QMenuBar::item:selected {

        background-color: #1e40af;
    }


    QMenu {

        background-color: #020617;
        border: 1px solid #334155;
    }


    QMenu::item:selected {

        background-color: #2563eb;
    }


    QStatusBar {

        background-color: #020617;
        color: #64ffda;
    }

    """)
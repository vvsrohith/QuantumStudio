import os


class Config:

    # ==========================================
    # Application Information
    # ==========================================

    APP_NAME = "Quantum Studio"

    VERSION = "1.0.0"

    AUTHOR = "V.V.S. Rohith"

    ORGANIZATION = "Quantum Playground"

    # ==========================================
    # Window
    # ==========================================

    WINDOW_WIDTH = 1400

    WINDOW_HEIGHT = 900

    MIN_WIDTH = 1200

    MIN_HEIGHT = 700

    # ==========================================
    # Quantum
    # ==========================================

    DEFAULT_QUBITS = 2

    MAX_QUBITS = 10

    DEFAULT_SHOTS = 1024

    # ==========================================
    # Supported Gates
    # ==========================================

    SINGLE_QUBIT_GATES = [

        "H",
        "X",
        "Y",
        "Z",
        "S",
        "T",
        "RX",
        "RY",
        "RZ"

    ]

    MULTI_QUBIT_GATES = [

        "CX",
        "CZ",
        "SWAP"

    ]

    SPECIAL_GATES = [

        "Measure",
        "Reset"

    ]

    ALL_GATES = (

        SINGLE_QUBIT_GATES +

        MULTI_QUBIT_GATES +

        SPECIAL_GATES

    )

    # ==========================================
    # Built-in Algorithms
    # ==========================================

    ALGORITHMS = [

        "Bell State",

        "GHZ State",

        "Quantum Teleportation",

        "Superdense Coding",

        "Deutsch",

        "Deutsch-Jozsa",

        "Bernstein-Vazirani",

        "Grover Search",

        "Quantum Fourier Transform",

        "Quantum Phase Estimation",

        "Shor Demonstration"

    ]

    # ==========================================
    # Directories
    # ==========================================

    BASE_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )

    ASSET_DIR = os.path.join(
        BASE_DIR,
        "assets"
    )

    EXPORT_DIR = os.path.join(
        BASE_DIR,
        "exports"
    )

    SAVE_DIR = os.path.join(
        BASE_DIR,
        "saved"
    )

    ICON_DIR = os.path.join(
        BASE_DIR,
        "icons"
    )

    # ==========================================
    # Images
    # ==========================================

    CIRCUIT_IMAGE = os.path.join(

        ASSET_DIR,

        "circuit.png"

    )

    HISTOGRAM_IMAGE = os.path.join(

        ASSET_DIR,

        "histogram.png"

    )

    PROBABILITY_IMAGE = os.path.join(

        ASSET_DIR,

        "probabilities.png"

    )

    BLOCH_IMAGE = os.path.join(

        ASSET_DIR,

        "bloch.png"

    )

    # ==========================================
    # Themes
    # ==========================================

    DEFAULT_THEME = "dark"

    AVAILABLE_THEMES = [

        "dark",

        "light",

        "ibm"

    ]

    # ==========================================
    # Export Formats
    # ==========================================

    EXPORT_FORMATS = [

        "PNG",

        "JSON",

        "TXT"

    ]

    # ==========================================
    # Console
    # ==========================================

    WELCOME_MESSAGE = """

==========================================

        Quantum Studio v1.0

Interactive Quantum Computing IDE

==========================================

Ready.

"""

    # ==========================================
    # Create Directories
    # ==========================================

    @staticmethod
    def initialize():

        os.makedirs(
            Config.ASSET_DIR,
            exist_ok=True
        )

        os.makedirs(
            Config.EXPORT_DIR,
            exist_ok=True
        )

        os.makedirs(
            Config.SAVE_DIR,
            exist_ok=True
        )

        os.makedirs(
            Config.ICON_DIR,
            exist_ok=True
        )
import sys
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quant Lab")

        layout = QVBoxLayout()
        label = QLabel("Quant Lab Running 🚀")
        layout.addWidget(label)

        self.setLayout(layout)

def run_ui():
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
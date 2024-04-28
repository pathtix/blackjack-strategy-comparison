from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QPushButton, QStackedWidget
)
from PyQt6.QtCore import Qt

class StatsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        label = QLabel('STATS SCREEN', self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
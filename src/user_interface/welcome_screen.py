from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class WelcomeScreen(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        label = QLabel("Welcome to the Blackjack Strategy Simulator", self)
        label_font = QFont("Arial", 24)
        label.setFont(label_font)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        button = QPushButton("Continue", self)
        button.clicked.connect(parent.show_main_screen)
        button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        button_font = QFont("Arial", 18)
        button.setFont(button_font)
        button.setMinimumSize(200, 50) 
        layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.setLayout(layout)

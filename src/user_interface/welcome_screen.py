from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class WelcomeScreen(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Add a vertical spacer at the top to push the content to the center
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        label = QLabel("Welcome to the Blackjack Strategy Simulator", self)
        label_font = QFont("Arial", 24)  # Increase the font size here
        label.setFont(label_font)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the label horizontally
        layout.addWidget(label)

        button = QPushButton("Continue", self)
        button.clicked.connect(parent.show_main_screen)  # Connect to the main window's method
        button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        button_font = QFont("Arial", 18)  # Increase the font size here
        button.setFont(button_font)
        button.setMinimumSize(200, 50)  # You can adjust the size as needed
        layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)  # Center the button horizontally

        # Add a vertical spacer at the bottom to ensure the button stays centered
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.setLayout(layout)

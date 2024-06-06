import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QPushButton, QStackedWidget
)
from PyQt6.QtCore import Qt

# Import your screen modules here. Make sure these are correctly implemented.
from simulation_screen import SimulationScreen
from stats_screen import StatsScreen
from settings_screen import SettingsScreen

class MainScreen(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        main_layout = QHBoxLayout(self.main_widget)
        sidebar = QVBoxLayout()
        main_content = QGridLayout()

        stacked_widget = QStackedWidget()
        stacked_widget.addWidget(SimulationScreen())
        stacked_widget.addWidget(StatsScreen())
        stacked_widget.addWidget(SettingsScreen())
        stacked_widget.setObjectName("StackedWidget")

        # Define the buttons
        simulations_button = self.create_button('Simulations', stacked_widget, 0)
        stats_button = self.create_button('Stats', stacked_widget, 1)
        settings_button = self.create_button('Settings', stacked_widget, 2)

        # Add buttons to the sidebar
        sidebar.addWidget(simulations_button)
        sidebar.addWidget(stats_button)
        sidebar.addWidget(settings_button)

        main_content.addWidget(stacked_widget)
        main_content.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add a frame around the sidebar to distinguish it from the content area
        sidebar_frame = QFrame()
        sidebar_frame.setFrameShape(QFrame.Shape.Box)
        sidebar_frame.setLayout(sidebar)
        sidebar_frame.setObjectName("SidebarFrame")

        content_frame = QFrame()
        content_frame.setFrameShape(QFrame.Shape.Box)
        content_frame.setLayout(main_content)
        content_frame.setObjectName("ContentFrame")

        main_layout.addWidget(sidebar_frame, 1)  # Sidebar takes less space
        main_layout.addWidget(content_frame, 6)  # Content takes more space

    def create_button(self, title, stacked_widget, index):
        button = QPushButton(title)
        button.setFixedSize(160, 50)
        button.clicked.connect(lambda: stacked_widget.setCurrentIndex(index))
        button.setStyleSheet("""
            QPushButton {
                font-family: 'Arial';
                background-color: #172636;
                color: white;
                padding: 5px;
                min-width: 80px;
                font-size: 14pt;
                color: white;
                border: 1px solid #172636;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0d1721;
            }
        """)
        return button

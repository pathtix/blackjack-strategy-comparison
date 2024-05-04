from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
import sys
from welcome_screen import WelcomeScreen
from main_screen import MainScreen

from simulation_screen import SimulationScreen
from stats_screen import StatsScreen
from settings_screen import SettingsScreen
from about_screen import AboutScreen

class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blackjack Strategy Simulator")
        self.setGeometry(100, 100, 1440, 900)  # x, y, width, height

        # Stacked widget to manage different screens
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create instances of the screens
        self.welcome_screen = WelcomeScreen(self)
        self.main_screen = MainScreen(self)


        # Add screens to the stacked widget
        self.stacked_widget.addWidget(self.welcome_screen)
        self.stacked_widget.addWidget(self.main_screen)

        
    def show_welcome_screen(self):
        self.stacked_widget.setCurrentWidget(self.welcome_screen)

    def show_main_screen(self):
        self.stacked_widget.setCurrentWidget(self.main_screen)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        #SidebarFrame {
            background-color: #172636;
        }
        #ContentFrame {
            background-color: #3a4556;
        }
        QMainWindow {
            background-color: #2d3848;
        }

    """)
    main_window = MainApplication()
    main_window.show()
    sys.exit(app.exec())

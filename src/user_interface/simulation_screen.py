from PyQt6.QtWidgets import QWidget, QGridLayout, QComboBox, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap, QMovie

from basic_strategy.basic_strategy import BasicStrategy
from basic_strategy.basic_strategy_with_counting import CountingStrategy

from brute_force.always_hit_bruteforce import AlwaysHitBruteForce
from brute_force.always_stand_bruteforce import AlwaysStandBruteForce
from brute_force.random_bruteforce import RandomBruteForce

from historical_data.historical_data import HistoricalData

from reincforment_learing.reincforcment_learning import ReinforcementLearning

from user_interface.simulation_worker import SimulationWorker

# $env:PYTHONPATH += ";C:\Users\genco\Desktop\blackjack-strategy-comparison\src"

class SimulationScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()

        self.gridAmount = 0
        self.threads = []  # List to hold active threads

        self.basic_strategy = BasicStrategy()
        self.counting_strategy = CountingStrategy()
        self.always_hit_bruteforce = AlwaysHitBruteForce()
        self.always_stand_bruteforce = AlwaysStandBruteForce()
        self.random_bruteforce = RandomBruteForce()
        self.historical_data = HistoricalData()
        self.rl_model = ReinforcementLearning()

        self.setStyleSheet("""
            #frame {
                background-color: #2d3848;
                border-radius: 5px;
            }
        """)

    def setupUI(self):
        self.layout = QGridLayout(self)
        self.layout.setSpacing(10)

        # Create the combo box and the button
        self.comboBox = QComboBox()
        self.comboBox.addItems([str(i) for i in range(1, 7)])
        self.comboBox.setFont(QFont('Arial', 12))  # Increase font size
        self.comboBox.setMinimumHeight(30)  # Increase the minimum height

        self.runButton = QPushButton("Run")
        self.runButton.setFont(QFont('Arial', 12))  # Increase font size
        self.runButton.setMinimumHeight(30)  # Increase the minimum height
        self.runButton.setStyleSheet("""
            QPushButton {
                background-color: #39aad1;
                padding: 5px;
                min-width: 80px;
                font-size: 14pt;
                border: 1px solid #39aad1;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #64c0df;
            }
        """)
        self.runButton.clicked.connect(self.drawSplittedScreen)

        # Add widgets to the grid
        self.layout.addWidget(self.comboBox, 0, 0)
        self.layout.addWidget(self.runButton, 0, 1)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Label for instructions or results
        self.label = QLabel("Select a number and click 'Run'.")
        self.layout.addWidget(self.label, 1, 0, 1, 2)  # Span both columns
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(QFont('Arial', 10))  # Font size for label

        self.setLayout(self.layout)

    def drawSplittedScreen(self):
        self.comboboxes = []

        selected_num = int(self.comboBox.currentText())
        print(f"{selected_num} was selected.")

        # Hide the combobox, run button, and label
        self.comboBox.setVisible(False)
        self.runButton.setVisible(False)
        self.label.setVisible(False)

        # Clear out any existing widgets in the layout
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Adjust row stretch
        # self.layout.setRowStretch(0, 0)  # No stretch for the first row where the combo and button were

        # Calculate the number of rows needed, assuming a max of 3 columns
        rows = (selected_num + 2) // 3
        columns = selected_num if selected_num < 3 else 3

        # Create and add new screen labels
        for i in range(selected_num):
            # Create frame and layout for individual simulation screen
            frame = QFrame(self)
            frame.setObjectName("frame")
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            frame_layout = QGridLayout(frame)
            frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Create ComboBox
            combobox = QComboBox(frame)
            combobox.addItems(["Always stand brute force", "Always hit brute force", "Random hit/stand brute force","Basic Strategy without counting", "Basic Strategy with counting", "Historical Data", "RL Model"])
            frame_layout.addWidget(combobox, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            self.comboboxes.append(combobox)

            play_button = QPushButton("▶", frame)
            play_button.setFont(QFont('Arial', 12))  # Set the font size to ensure the button is square
            play_button.setStyleSheet("""
                QPushButton {
                    font-size: 14pt;
                    border-radius: 15px;
                    min-width: 30px;
                    min-height: 30px;
                    max-width: 30px;
                    max-height: 30px;
                }
                QPushButton:hover {
                    background-color: #64c0df;
                }
            """)
            frame_layout.addWidget(play_button, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)


            # Connect the button's clicked signal
            play_button.clicked.connect(lambda ch, index=i: self.run_script(index))

            # Calculate row and column
            row = (i // columns) + 1  # Start adding from the second row
            column = i % columns
            self.layout.addWidget(frame, row, column)

        # Adjust row stretch for any additional empty rows
        for i in range(rows):
            self.layout.setRowStretch(i + 1, 1)  # Add 1 for the spacer item row

        # Adjust column stretch for columns
        for i in range(columns):
            self.layout.setColumnStretch(i, 1)

    def run_script(self, index):
        combobox = self.comboboxes[index]
        script_name = combobox.currentText()
        print(f"Run button for combobox at index {index} clicked to run script: {script_name}")



        script_functions = {
            "Always hit brute force": self.always_hit_bruteforce.output_results,
            "Always stand brute force": self.always_stand_bruteforce.output_results,
            "Random hit/stand brute force": self.random_bruteforce.output_results,
            "Basic Strategy without counting" : self.basic_strategy.output_results,
            "Basic Strategy with counting" : self.counting_strategy.output_results,
            "Historical Data": self.historical_data.output_results,
            "RL Model": self.rl_model.output_results
        }

        function_to_run = script_functions.get(script_name)

        if function_to_run:
            # Create a thread to run the simulation
            worker = SimulationWorker(function_to_run)
            worker.finished.connect(self.on_simulation_complete)
            worker.finished.connect(worker.deleteLater)  # Ensure thread cleanup
            self.threads.append(worker)  # Keep track of the thread
            worker.start()  # Start the thread
            

    def setting_script(self, index):
        combobox = self.comboboxes[index]
        script_name = combobox.currentText()
        print(f"Setting button for combobox at index {index}")

    def on_simulation_complete(self, message):
        print("Simulation completed with message:", message)

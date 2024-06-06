from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QPushButton, QStackedWidget, QComboBox, QCheckBox,
    QSplitter, QSizePolicy, QTableWidget, QTableWidgetItem, QLineEdit
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

import pandas as pd
from openpyxl import load_workbook

from graph_screen import GraphWindow

class StatsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_simulation_number = 0
        self.working_path = ''
        self.df = None

        self.graph_windows = []

        self.setupUI()
        self.setStyleSheet("""
            #left_frame {
                background-color: #2d3848;
                border-radius: 5px;
            }

            #right_frame {
                background-color: #2d3848;
                border-radius: 5px;
            }

            #table_frame {
                background-color: #2d3848;
                border-radius: 5px;
            }
            """
        )

    def setupUI(self):
        # Main vertical layout
        main_layout = QVBoxLayout(self)

        # Create the splitter to make the bottom frame resizable
        top_frame = QFrame()
        bottom_frame = QFrame()

        # Top layout container
        top_layout = QHBoxLayout(top_frame)
        bottom_layout = QHBoxLayout(bottom_frame)

        max_width = 1440
        max_height = 320

        top_frame.setMaximumSize(QSize(max_width, max_height))

        # Left frame for "Data to shown"
        left_frame = QFrame()
        left_frame.setObjectName("left_frame")
        left_frame.setFrameShape(QFrame.Shape.StyledPanel)
        left_layout = QVBoxLayout(left_frame)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        top_layout.addWidget(left_frame)

        self.data_combo = QComboBox()
        self.data_combo.setFont(QFont('Arial', 10))
        self.data_combo.addItems(['ALWAYS_HIT', 'ALWAYS_STAND', 'RANDOM_HIT_STAND', 'BASIC_STRATEGY_WITHOUTCOUNTING', 'BASIC_STRATEGY_WITHCOUNTING', 'HISTORICAL_DATA', 'RL_MODEL'])  # Add more options as needed
        left_layout.addWidget(self.data_combo)

        load_data_button = QPushButton("Load Data")
        load_data_button.setFont(QFont('Arial', 10))
        load_data_button.clicked.connect(self.load_data)
        load_data_button.setStyleSheet("""
            QPushButton {
                background-color: #39aad1;
                padding: 5px;
                min-width: 40px;
                font-size: 12pt;
                border: 1px solid #39aad1;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #64c0df;
            }
        """)
        left_layout.addWidget(load_data_button)

        # Right frame for model selection and axes settings
        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.Shape.StyledPanel)
        right_frame.setObjectName("right_frame")

        right_layout = QVBoxLayout(right_frame)
        top_layout.addWidget(right_frame)

        models_label = QLabel("Models")
        models_label.setFont(QFont('Arial', 10))
        models_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(models_label)

        self.model_checkboxes = []
        models_list = ['ALWAYS_HIT', 'ALWAYS_STAND', 'RANDOM_HIT_STAND', 'BASIC_STRATEGY_WITHOUTCOUNTING', 'BASIC_STRATEGY_WITHCOUNTING', 'HISTORICAL_DATA', 'RL_MODEL']
        for model in models_list:
            check_box = QCheckBox(model)
            right_layout.addWidget(check_box)
            self.model_checkboxes.append(check_box)

        x_axis_layout = QHBoxLayout()
        x_axis_label = QLabel("X-axis:")
        self.x_axis_combo = QComboBox()
        self.x_axis_combo.addItems(['Money', 'Games Played per Simulation', 'Total Simulations', 'Simulation'])  # Add more options as needed
        x_axis_layout.addWidget(x_axis_label)
        x_axis_layout.addWidget(self.x_axis_combo)
        right_layout.addLayout(x_axis_layout)

        y_axis_layout = QHBoxLayout()
        y_axis_label = QLabel("Y-axis:")
        self.y_axis_combo = QComboBox()
        self.y_axis_combo.addItems(['Win Rate', 'Loss Rate', 'Games Played per Simulation', 'Money', 'Total Simulations', 'Average ROI'])  # Add more options as needed
        y_axis_layout.addWidget(y_axis_label)
        y_axis_layout.addWidget(self.y_axis_combo)
        right_layout.addLayout(y_axis_layout)

        generate_button = QPushButton("Generate Graph")
        generate_button.clicked.connect(self.generate_graph)
        generate_button.setStyleSheet("""
            QPushButton {
                background-color: #39aad1;
                padding: 5px;
                min-width: 40px;
                font-size: 12pt;
                border: 1px solid #39aad1;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #64c0df;
            }
        """)
        right_layout.addWidget(generate_button)

        # Configure the bottom frame
        self.table_frame = QFrame()
        self.table_frame.setObjectName("table_frame")
        self.table_frame.setLayout(QVBoxLayout())
        self.table_frame.setFrameShape(QFrame.Shape.StyledPanel)

        bottom_layout.addWidget(self.table_frame)

        main_layout.addWidget(top_frame)
        main_layout.addWidget(bottom_frame)

        # Set the layout to the main widget
        self.setLayout(main_layout)

    def generate_graph(self):
        selected_models = [checkbox.text() for checkbox in self.model_checkboxes if checkbox.isChecked()]
        x_axis = self.x_axis_combo.currentText()
        y_axis = self.y_axis_combo.currentText()

        print(f"Selected models: {selected_models}")
        print(f"X-axis: {x_axis}, Y-axis: {y_axis}")

        self.graph_window = GraphWindow(selected_models=selected_models, x_param=x_axis, y_param=y_axis)

        self.destroyed.connect(self.graph_window.close)
        self.graph_window.show()
        self.graph_windows.append(self.graph_window)

    def load_data(self):
        selected_model = self.data_combo.currentText()
        self.current_simulation_number = 0 # to reset back to page 0 when loading new data

        print(f"Loading data for model: {selected_model}")
        # Load the entire DataFrame for the selected model
        match selected_model:
            case 'ALWAYS_HIT':
                self.working_path = 'src/brute_force/always_hit_results/always_hit_results.xlsx'
            case 'ALWAYS_STAND':
                self.working_path = 'src/brute_force/always_stand_results/always_stand_results.xlsx'
            case 'RANDOM_HIT_STAND':
                self.working_path = 'src/brute_force/random_hitstand_results/random_hitstand_results.xlsx'
            case 'BASIC_STRATEGY_WITHOUTCOUNTING':
                self.working_path = 'src/basic_strategy/basic_strategy_results/basic_strategy_results.xlsx'
            case 'BASIC_STRATEGY_WITHCOUNTING':
                self.working_path = 'src/basic_strategy/counting_strategy_results/counting_strategy_results.xlsx'
            case 'HISTORICAL_DATA':
                self.working_path = 'src/historical_data/historical_data_results/historical_data_results.xlsx'
            case 'RL_MODEL':
                self.working_path = 'src/reincforment_learing/reincforment_learing_results/reincforment_learing_results.xlsx'

        # Load the entire DataFrame
        self.df = pd.read_excel(self.working_path)

        # Display the first simulation
        self.display_simulation(self.current_simulation_number)

    def display_simulation(self, simulation_number):
        if self.df is not None:
            df_filtered = self.df[self.df['Simulation'] == simulation_number]
            self.display_dataframe(df_filtered)

    def display_dataframe(self, df):
        if hasattr(self, 'table_widget'):
            self.table_widget.clear()
            self.table_widget.setRowCount(df.shape[0])
            self.table_widget.setColumnCount(df.shape[1])
            self.table_widget.setHorizontalHeaderLabels(df.columns)
        else:
            self.table_widget = QTableWidget(self.table_frame)
            self.table_widget.setRowCount(df.shape[0])
            self.table_widget.setColumnCount(df.shape[1])
            self.table_widget.setHorizontalHeaderLabels(df.columns)
            print("Table created")
            self.display_table_buttons()

        # Populate the table with items
        for row in range(df.shape[0]):
            for column in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iat[row, column]))
                self.table_widget.setItem(row, column, item)

        self.table_frame.layout().addWidget(self.table_widget)  # Add the table to the layout
        self.table_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)  # Set size policy
        self.table_widget.show()

        self.update_button_states()

    def display_table_buttons(self):
        button_layout = QHBoxLayout()
        self.table_frame.layout().addLayout(button_layout)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_table)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #39aad1;
                padding: 5px;
                min-width: 40px;
                font-size: 12pt;
                border: 1px solid #39aad1;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #64c0df;
            }
        """)
        button_layout.addWidget(self.clear_button)

        self.previous_button = QPushButton("Previous")
        self.previous_button.clicked.connect(self.previous_simulation)
        self.previous_button.setStyleSheet("""
            QPushButton {
                background-color: #39aad1;
                padding: 5px;
                min-width: 40px;
                font-size: 12pt;
                border: 1px solid #39aad1;
                border-radius: 5px;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #aaaaaa;
                border: 1px solid #444444;
            }
            QPushButton:hover {
                background-color: #64c0df;
            }
        """)
        button_layout.addWidget(self.previous_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_simulation)
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: #39aad1;
                padding: 5px;
                min-width: 40px;
                font-size: 12pt;
                border: 1px solid #39aad1;
                border-radius: 5px;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #aaaaaa;
                border: 1px solid #444444;
            }
            QPushButton:hover {
                background-color: #64c0df;
            }
        """)
        button_layout.addWidget(self.next_button)

        self.goto_input = QLineEdit()
        self.goto_input.setFont(QFont('Arial', 18))
        self.goto_input.setFixedWidth(50)
        button_layout.addWidget(self.goto_input)

        self.goto_button = QPushButton("Go To")
        self.goto_button.clicked.connect(self.goto_simulation)
        self.goto_button.setStyleSheet("""
            QPushButton {
                background-color: #39aad1;
                padding: 5px;
                min-width: 40px;
                font-size: 12pt;
                border: 1px solid #39aad1;
                border-radius: 5px;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #aaaaaa;
                border: 1px solid #444444;
            }
            QPushButton:hover {
                background-color: #64c0df;
            }
        """)
        button_layout.addWidget(self.goto_button)

    def next_simulation(self):
        total_simulations = self.df['Simulation'].nunique()

        if self.current_simulation_number < total_simulations - 1:
            self.current_simulation_number += 1
        else:
            self.current_simulation_number = 0  # Optionally reset to the first simulation or handle differently

        print(f"Loading data for simulation number: {self.current_simulation_number}")
        self.display_simulation(self.current_simulation_number)

    def previous_simulation(self):
        total_simulations = self.df['Simulation'].nunique()

        if self.current_simulation_number > 0:
            self.current_simulation_number -= 1
        else:
            self.current_simulation_number = total_simulations - 1  # Optionally reset to the last simulation or handle differently

        print(f"Loading data for simulation number: {self.current_simulation_number}")
        self.display_simulation(self.current_simulation_number)

    def goto_simulation(self):
        try:
            simulation_number = int(self.goto_input.text())
            if 0 <= simulation_number < self.df['Simulation'].nunique():
                self.current_simulation_number = simulation_number
                print(f"Loading data for simulation number: {self.current_simulation_number}")
                self.display_simulation(self.current_simulation_number)
            else:
                print("Invalid simulation number.")
        except ValueError:
            print("Invalid input. Please enter a valid simulation number.")

    def clear_table(self):
        self.table_widget.clear()
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(0)
        self.table_widget.hide()
        self.table_widget.deleteLater()
        del self.table_widget

        self.clear_button.hide()
        self.clear_button.deleteLater()
        del self.clear_button

        self.next_button.hide()
        self.next_button.deleteLater()
        del self.next_button

        self.previous_button.hide()
        self.previous_button.deleteLater()
        del self.previous_button

        self.goto_input.hide()
        self.goto_input.deleteLater()
        del self.goto_input

        self.goto_button.hide()
        self.goto_button.deleteLater()
        del self.goto_button

    def update_button_states(self):
        total_simulations = self.df['Simulation'].nunique()

        # Disable the "Previous" button if on the first simulation, enable otherwise
        self.previous_button.setEnabled(self.current_simulation_number > 0)

        # Disable the "Next" button if on the last simulation, enable otherwise
        self.next_button.setEnabled(self.current_simulation_number < total_simulations - 1)

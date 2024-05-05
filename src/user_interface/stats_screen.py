from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QGridLayout, QPushButton, QStackedWidget, QComboBox, QCheckBox,
    QSplitter, QSizePolicy, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

import pandas as pd
from openpyxl import load_workbook

from graph_screen import GraphWindow

class StatsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_sheet_number = 0
        self.working_path = ''

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
        self.data_combo.addItems(['Always hit', 'Always stand', 'Random hit/stand', 'Basic strategy with counting', 'Basic strategy without counting', 'Historical Data', 'RL Model'])  # Add more options as needed
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
        models_list = ['Always hit', 'Always stand', 'Random hit/stand', 'Basic strategy with counting', 'Basic strategy without counting', 'Historical Data', 'RL Model']
        for model in models_list:
            check_box = QCheckBox(model)
            right_layout.addWidget(check_box)
            self.model_checkboxes.append(check_box)

        x_axis_layout = QHBoxLayout()
        x_axis_label = QLabel("X-axis:")
        self.x_axis_combo = QComboBox()
        self.x_axis_combo.addItems(['Money', 'Games played', 'Wins'])  # Add more options as needed
        x_axis_layout.addWidget(x_axis_label)
        x_axis_layout.addWidget(self.x_axis_combo)
        right_layout.addLayout(x_axis_layout)

        y_axis_layout = QHBoxLayout()
        y_axis_label = QLabel("Y-axis:")
        self.y_axis_combo = QComboBox()
        self.y_axis_combo.addItems(['Win rate', 'Loss rate', 'Draw rate'])  # Add more options as needed
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
        self.current_sheet_number = 0 # to reset back to page 0 when loading new data

        print(f"Loading data for model: {selected_model}")

        match selected_model:
            case 'Always hit':
                self.working_path = 'brute_force/always_hit_results/always_hit_results.xlsx'
                print(f"Always hit model has {self.get_number_of_sheets(self.working_path)} sheets, oppening sheet {self.current_sheet_number}")
                df = pd.read_excel(self.working_path, sheet_name='test' + str(self.current_sheet_number))
                self.display_dataframe(df)
            case 'Always stand':
                self.working_path = 'brute_force/always_stand_results/always_stand_results.xlsx'
                print(f"Always hit model has {self.get_number_of_sheets(self.working_path)} sheets, oppening sheet {self.current_sheet_number}")
                df = pd.read_excel(self.working_path, sheet_name='test' + str(self.current_sheet_number))
                self.display_dataframe(df)
            case 'Random hit/stand':
                self.working_path = 'brute_force/random_hitstand_results/random_hitstand_results.xlsx'
                print(f"Always hit model has {self.get_number_of_sheets(self.working_path)} sheets, oppening sheet {self.current_sheet_number}")
                df = pd.read_excel(self.working_path, sheet_name='test' + str(self.current_sheet_number))
                self.display_dataframe(df)
            case 'Basic strategy with counting': # TODO: Implement basic strategy with counting
                self.working_path = 'basic_strategy/basic_strategy_results/basic_strategy_results.xlsx'
                print(f"Always hit model has {self.get_number_of_sheets(self.working_path)} sheets, oppening sheet {self.current_sheet_number}")
                df = pd.read_excel(self.working_path, sheet_name='test' + str(self.current_sheet_number))
                self.display_dataframe(df)
            case 'Basic strategy without counting':
                self.working_path = 'basic_strategy/basic_strategy_results/basic_strategy_results.xlsx'
                print(f"Always hit model has {self.get_number_of_sheets(self.working_path)} sheets, oppening sheet {self.current_sheet_number}")
                df = pd.read_excel(self.working_path, sheet_name='test' + str(self.current_sheet_number))
                self.display_dataframe(df)
            case 'Historical Data':
                self.working_path = 'historical_data/historical_data_results/historical_data_results.xlsx'
                print(f"Always hit model has {self.get_number_of_sheets(self.working_path)} sheets, oppening sheet {self.current_sheet_number}")
                df = pd.read_excel(self.working_path, sheet_name='test' + str(self.current_sheet_number))
                self.display_dataframe(df)
            case 'RL Model':
                print("Loading data for RL model")

    def get_number_of_sheets(self ,file_path):
        workbook = load_workbook(filename= file_path, read_only=True)
        return len(workbook.sheetnames)
    
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

        """
        if hasattr(self, 'table_widget'):
            self.table_widget.clear()
            self.table_widget.setRowCount(0)
            self.table_widget.setColumnCount(0)
            print("Table cleared")

        """
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
        self.previous_button.clicked.connect(self.previous_sheet)
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
        self.next_button.clicked.connect(self.next_sheet)
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



    def next_sheet(self):
        workbook_path = self.working_path
        total_sheets = self.get_number_of_sheets(workbook_path)

        # Increment the current sheet number and wrap around if necessary
        if self.current_sheet_number < total_sheets - 2:
            self.current_sheet_number += 1
        else:
            self.current_sheet_number = 0  # Optionally reset to the first sheet or handle differently

        # Reload data from the new sheet
        print(f"Loading data from sheet number: {self.current_sheet_number}")
        df = pd.read_excel(workbook_path, sheet_name='test' + str(self.current_sheet_number))
        self.display_dataframe(df)

    def previous_sheet(self):
        workbook_path = self.working_path
        total_sheets = self.get_number_of_sheets(workbook_path)

        # Decrement the current sheet number and wrap around if necessary
        if self.current_sheet_number > 0:
            self.current_sheet_number -= 1
        else:
            self.current_sheet_number = total_sheets - 2  # Optionally reset to the last sheet or handle differently

        # Reload data from the new sheet
        print(f"Loading data from sheet number: {self.current_sheet_number}")
        df = pd.read_excel(workbook_path, sheet_name='test' + str(self.current_sheet_number))
        self.display_dataframe(df)

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

    def update_button_states(self):
        workbook_path = self.working_path
        total_sheets = self.get_number_of_sheets(workbook_path)

        # Disable the "Previous" button if on the first sheet, enable otherwise
        self.previous_button.setEnabled(self.current_sheet_number > 0)

        # Disable the "Next" button if on the last sheet, enable otherwise
        self.next_button.setEnabled(self.current_sheet_number < total_sheets - 2)
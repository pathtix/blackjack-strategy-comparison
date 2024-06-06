import os
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QFormLayout, QLineEdit, QPushButton, QSpinBox, QCheckBox, QFileDialog, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from settings import (
    AlwaysHitBruteForceSettings, AlwaysStandBruteForceSettings,
    RandomHitStandBruteForceSettings, BasicStrategyWithCountingSettings,
    BasicStrategyWithoutCountingSettings, HistoricalDataSettings, RLSettings
)

from reincforment_learing.model_training import BlackjackEnv
class SettingsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.model_parameters = {
            "Always stand brute force": [("Initial Money", QLineEdit), ("Simulation Amount", QLineEdit),("Bet Amount", QLineEdit)],
            "Always hit brute force": [("Initial Money", QLineEdit), ("Simulation Amount", QLineEdit), ("Threshold", QLineEdit),("Bet Amount", QLineEdit)],
            "Random hit/stand": [("Initial Money", QLineEdit), ("Simulation Amount", QLineEdit),("Bet Amount", QLineEdit)],
            "Basic strategy without counting": [("Initial Money", QLineEdit), ("Simulation Amount", QLineEdit), ("Is doubleing allowed", QCheckBox),("Bet Amount", QLineEdit)],
            "Basic strategy with counting": [("Initial Money", QLineEdit), ("Simulation Amount", QLineEdit), ("Is doubleing allowed", QCheckBox), ("Minimum Bet", QLineEdit), ("Maximum Bet", QLineEdit)],
            "Historical data": [("Initial Money", QLineEdit), ("Simulation Amount", QLineEdit), ("Database path", QLineEdit), ("Is doubleing allowed", QCheckBox),("Bet Amount", QLineEdit)],
            "Reinforcement learning": [("Initial Money", QLineEdit), ("Simulation Amount", QLineEdit), ("Bet Amount", QLineEdit),  ("Q Table Path", QLineEdit), ("Alpha", QLineEdit), ("Gamma", QLineEdit), ("Epsilon", QLineEdit), ("Number of Episodes", QLineEdit)]
        }

        self.settings_widgets = {}  # New dictionary to store widget references
        self.setupUI()

    def setupUI(self):
        main_layout = QVBoxLayout(self)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { background-color: #3a4556; border: none; }")  # Set the scroll area background
        main_layout.addWidget(scroll_area)

        scroll_container = QWidget()
        scroll_container.setStyleSheet("background-color: #3a4556; ")
        scroll_area.setWidget(scroll_container)

        container_layout = QVBoxLayout(scroll_container)

        for model, parameters in self.model_parameters.items():
            model_frame = QFrame(scroll_container)
            model_frame.setFrameShape(QFrame.Shape.StyledPanel)

            model_frame_layout = QVBoxLayout(model_frame)
            title = QLabel(model)
            title.setFont(QFont('Arial', 16))
            model_frame_layout.addWidget(title)
            model_frame.setStyleSheet("QFrame { background-color: #2d3848; border-radius: 5px; }")  # Set the frame background and border
            settings_layout = QFormLayout()

            self.settings_widgets[model] = {}

            for param_name, widget_cls in parameters:
                if param_name == "Q Table Path":
                    file_selector_layout = QHBoxLayout()
                    line_edit = QLineEdit()
                    browse_button = QPushButton("Browse")
                    browse_button.setStyleSheet("QPushButton { color: white;  border-radius: 5px; } QPushButton:hover {background-color: #4d94ac;}")
                    browse_button.clicked.connect(lambda _, le=line_edit: self.select_q_table_path(le))

                    file_selector_layout.addWidget(line_edit)
                    file_selector_layout.addWidget(browse_button)
                    self.settings_widgets[model][param_name] = line_edit

                    settings_layout.addRow(param_name + ":", file_selector_layout)
                elif param_name == "Database path":
                    file_selector_layout = QHBoxLayout()
                    line_edit = QLineEdit()
                    browse_button = QPushButton("Browse")
                    browse_button.setStyleSheet("QPushButton { color: white;  border-radius: 5px; } QPushButton:hover {background-color: #4d94ac;}")
                    browse_button.clicked.connect(lambda _, le=line_edit: self.select_database_path(le))

                    file_selector_layout.addWidget(line_edit)
                    file_selector_layout.addWidget(browse_button)
                    self.settings_widgets[model][param_name] = line_edit

                    settings_layout.addRow(param_name + ":", file_selector_layout)
                else:
                    widget = widget_cls()  # Create an instance of the widget class
                    self.settings_widgets[model][param_name] = widget  # Store the widget reference

                    widget.setStyleSheet("background-color: #3a4556; color: white; border-radius: 5px;")  # Set the widget background and border
                    if widget_cls == QCheckBox:
                        widget.setText(param_name)
                        settings_layout.addRow(widget)
                    else:
                        settings_layout.addRow(param_name + ":", widget)

            apply_button = QPushButton("Apply")
            reset_button = QPushButton("Reset")

            # Style the buttons
            apply_button.setStyleSheet("QPushButton { color: white;  border-radius: 5px; } QPushButton:hover {background-color: #4d94ac;}")
            reset_button.setStyleSheet("QPushButton { color: white;  border-radius: 5px; } QPushButton:hover {background-color: #4d94ac;}")

            # Connect the apply button's clicked signal
            apply_button.clicked.connect(lambda ch, m=model: self.apply_settings(m))
            reset_button.clicked.connect(lambda ch, m=model: self.reset_settings(m))

            # Add buttons to the settings layout
            settings_layout.addRow(reset_button, apply_button)

            if model == "Reinforcement learning":
                create_button = QPushButton("Create")
                create_button.setStyleSheet("QPushButton { color: white;  border-radius: 5px; } QPushButton:hover {background-color: #4d94ac;}")
                create_button.clicked.connect(self.create_rl_model)
                settings_layout.addRow(create_button)

            model_frame_layout.addLayout(settings_layout)
            container_layout.addWidget(model_frame)

        container_layout.addStretch()

        self.setLayout(main_layout)

    def select_q_table_path(self, line_edit):
        file_dialog = QFileDialog()
        q_table_path, _ = file_dialog.getOpenFileName(self, "Select Q Table Path", "", "Pickle Files (*.pkl);;All Files (*)")
        if q_table_path:
            line_edit.setText(q_table_path)

    def select_database_path(self, line_edit):
        file_dialog = QFileDialog()
        database_path, _ = file_dialog.getOpenFileName(self, "Select Database Path", "","Database Files (*.db);;All Files (*)")
        if database_path:
            line_edit.setText(database_path)

    def create_rl_model(self):
        model_widgets = self.settings_widgets.get("Reinforcement learning", {})

        alpha = float(model_widgets["Alpha"].text())
        gamma = float(model_widgets["Gamma"].text())
        epsilon = float(model_widgets["Epsilon"].text())
        num_episodes = int(model_widgets["Number of Episodes"].text())

        try:
            training = BlackjackEnv(alpha, gamma, epsilon, num_episodes)
            training.fill_q_table()
            training.train_model()
            training.save_q_table()
            print("Model training script executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while executing the model training script: {e}")

    def apply_settings(self, model_name):
        print(f"Applied settings for model {model_name}")

        # Retrieve the widgets for this model
        model_widgets = self.settings_widgets.get(model_name, {})

        for param_name, widget in model_widgets.items():
            if isinstance(widget, QLineEdit):
                if widget.text() != '':
                    print(f"Parameter: {param_name}, Value: {widget.text()}")
                    if param_name == 'Threshold':
                        AlwaysHitBruteForceSettings['Threshold'] = int(widget.text())
                    if param_name == 'Simulation Amount':
                        match model_name:
                            case "Always stand brute force":
                                AlwaysStandBruteForceSettings['Simulation Amount'] = int(widget.text())
                            case "Always hit brute force":
                                AlwaysHitBruteForceSettings['Simulation Amount'] = int(widget.text())
                            case "Random hit/stand":
                                RandomHitStandBruteForceSettings['Simulation Amount'] = int(widget.text())
                            case "Basic strategy without counting":
                                BasicStrategyWithoutCountingSettings['Simulation Amount'] = int(widget.text())
                            case "Basic strategy with counting":
                                BasicStrategyWithCountingSettings['Simulation Amount'] = int(widget.text())
                            case "Historical data":
                                HistoricalDataSettings['Simulation Amount'] = int(widget.text())
                            case "Reinforcement learning":
                                RLSettings['Simulation Amount'] = int(widget.text())
                    if param_name == 'Initial Money':
                        match model_name:
                            case "Always stand brute force":
                                AlwaysStandBruteForceSettings['Initial Money'] = int(widget.text())
                            case "Always hit brute force":
                                AlwaysHitBruteForceSettings['Initial Money'] = int(widget.text())
                            case "Random hit/stand":
                                RandomHitStandBruteForceSettings['Initial Money'] = int(widget.text())
                            case "Basic strategy without counting":
                                BasicStrategyWithoutCountingSettings['Initial Money'] = int(widget.text())
                            case "Basic strategy with counting":
                                BasicStrategyWithCountingSettings['Initial Money'] = int(widget.text())
                            case "Historical data":
                                HistoricalDataSettings['Initial Money'] = int(widget.text())
                            case "Reinforcement learning":
                                RLSettings['Initial Money'] = int(widget.text())
                    if param_name == "Bet Amount":
                        match model_name:
                            case "Always stand brute force":
                                AlwaysStandBruteForceSettings['Bet Amount'] = int(widget.text())
                            case "Always hit brute force":
                                AlwaysHitBruteForceSettings['Bet Amount'] = int(widget.text())
                            case "Random hit/stand":
                                RandomHitStandBruteForceSettings['Bet Amount'] = int(widget.text())
                            case "Basic strategy without counting":
                                BasicStrategyWithoutCountingSettings['Bet Amount'] = int(widget.text())
                            case "Historical data":
                                HistoricalDataSettings['Bet Amount'] = int(widget.text())
                            case "Reinforcement learning":
                                RLSettings['Bet Amount'] = int(widget.text())
                    if param_name == "Minimum Bet":
                        BasicStrategyWithCountingSettings['Minimum Bet'] = int(widget.text())
                    if param_name == "Maximum Bet":
                        BasicStrategyWithCountingSettings['Maximum Bet'] = int(widget.text())
                    if param_name == 'Data source':
                        HistoricalDataSettings['Data Source'] = widget.text()
                    if param_name == 'Database Path':
                        HistoricalDataSettings['Database Path'] = widget.text()
                    if param_name == 'Q Table Path':
                        RLSettings['Q Table Path'] = widget.text()
                    if param_name == 'Alpha':
                        RLSettings['Alpha'] = float(widget.text())
                    if param_name == 'Gamma':
                        RLSettings['Gamma'] = float(widget.text())
                    if param_name == 'Epsilon':
                        RLSettings['Epsilon'] = float(widget.text())
                    if param_name == 'Number of Episodes':
                        RLSettings['Number of Episodes'] = int(widget.text())

            elif isinstance(widget, QCheckBox):
                print(f"Parameter: {param_name}, Checked: {widget.isChecked()}")
                if param_name == 'Doubleing Allowed':
                    match model_name:
                        case "Basic strategy without counting":
                            BasicStrategyWithoutCountingSettings['Doubleing Allowed'] = widget.isChecked()
                        case "Basic strategy with counting":
                            BasicStrategyWithCountingSettings['Doubleing Allowed'] = widget.isChecked()

    def reset_settings(self, model_name):
        print(f"Reset settings for model {model_name}")

        # Retrieve the widgets for this model
        model_widgets = self.settings_widgets.get(model_name, {})

        for param_name, widget in model_widgets.items():
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, QCheckBox):
                widget.setChecked(False)

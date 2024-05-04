from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QFormLayout, QLineEdit, QPushButton, QSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from settings import (
    AlwaysHitBruteForceSettings, AlwaysStandBruteForceSettings, RandomHitStandBruteForceSettings, BasicStrategyWithCountingSettings, BasicStrategyWithoutCountingSettings, HistoricalDataSettings
)

class SettingsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.model_parameters = {
            "Always stand brute force": [("Simulation Amount", QLineEdit)],
            "Always hit brute force": [("Simulation Amount", QLineEdit), (("Threshold", QLineEdit))],
            "Random hit/stand": [("Simulation Amount", QLineEdit)],
            "Basic strategy without counting": [("Simulation Amount", QLineEdit), ("Soft 17 rule", QCheckBox), ("Is doubleing allowed", QCheckBox)],
            "Basic strategy with counting": [("Simulation Amount", QLineEdit), ("Soft 17 rule", QCheckBox),  ("Is doubleing allowed", QCheckBox), ("Counting system", QLineEdit)],
            "Historical data": [("Simulation Amount", QLineEdit), ("Data source", QLineEdit)]
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
                widget = widget_cls()  # Create an instance of the widget class
                self.settings_widgets[model][param_name] = widget  # Store the widget reference
                
                widget.setStyleSheet("background-color: #3a4556; color: white; border-radius: 5px;")  # Set the widget background and border
                if widget_cls == QCheckBox:
                    widget.setText(param_name)
                    settings_layout.addRow(widget)
                else:
                    settings_layout.addRow(param_name+":", widget)
            
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

            model_frame_layout.addLayout(settings_layout)
            container_layout.addWidget(model_frame)

        container_layout.addStretch()

        self.setLayout(main_layout)

    def apply_settings(self, model_name):
        print(f"Applied settings for model {model_name}")

        # Retrieve the widgets for this model
        model_widgets = self.settings_widgets.get(model_name, {})

        for param_name, widget in model_widgets.items():
            if isinstance(widget, QLineEdit):
                if (widget.text() != ''):
                    print(f"Parameter: {param_name}, Value: {widget.text()}")
                    if (param_name == 'Threshold'):
                        AlwaysHitBruteForceSettings['Threshold'] = int(widget.text())
                    if (param_name == 'Simulation Amount'):
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
                    if (param_name == 'Data source'):
                        HistoricalDataSettings['Data Source'] = widget.text()

            elif isinstance(widget, QCheckBox):
                print(f"Parameter: {param_name}, Checked: {widget.isChecked()}")
            # Handle other widget types as needed

    def reset_settings(self, model_name):
        print(f"Settings resetted for {model_name}")
        # Here you would access the specific settings for this model and apply them
        # For example, iterate through self.model_parameters[model_name] to find the widgets and retrieve their values
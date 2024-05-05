from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame, QScrollArea, QGridLayout
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

class GraphWindow(QWidget):
    def __init__(self, selected_models, x_param, y_param, parent=None):
        super().__init__(parent)
        self.selected_models = selected_models
        self.x_param = x_param
        self.y_param = y_param
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: #3a4556;")  # Set the background color of the window

        layout = QVBoxLayout()
        scroll_area = QScrollArea(self)  # Use a scroll area to manage multiple graphs
        scroll_widget = QWidget()  # This widget will contain all the frames
        grid_layout = QGridLayout(scroll_widget)

        # Number of columns is fixed to 3 for your case
        cols = 3
        num_models = len(self.selected_models)
        rows = (num_models + cols - 1) // cols  # Calculate required rows

        for index, model_name in enumerate(self.selected_models):
            frame = QFrame(scroll_widget)
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            frame.setStyleSheet("QFrame { background-color: #2d3848; border-radius: 5px; }")  # Set the frame color
            frame_layout = QVBoxLayout()
            self.add_graph_to_frame(frame_layout, model_name, self.x_param, self.y_param)
            frame.setLayout(frame_layout)
            grid_layout.addWidget(frame, index // cols, index % cols)

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        self.setLayout(layout)

        # Set the window height dynamically based on the number of rows
        base_height = 400  # Height for one row
        self.resize(1200, base_height * rows)  # Adjust width if necessary

        self.setWindowTitle('Graphs')

    def add_graph_to_frame(self, layout, model_name, x_param, y_param):
        # Create the graph using Matplotlib
        fig, ax = plt.subplots()
        ax.plot([0, 1, 2, 3], [10, 20, 10, 30])  # Placeholder for actual data
        ax.set_title(f'{model_name} - {x_param} vs. {y_param}')
        ax.set_xlabel(x_param)
        ax.set_ylabel(y_param)

        # Embedding Matplotlib graph into a PyQt widget
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)

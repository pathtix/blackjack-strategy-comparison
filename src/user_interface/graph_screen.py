from PyQt6.QtWidgets import QMainWindow

class GraphWindow(QMainWindow):
    def __init__(self, selected_models = [], x_axis = "", y_axis = ""):
        super().__init__()
        self.setWindowTitle("Graph Window")
        self.setGeometry(100, 100, 1280, 720)

        self.selected_models = selected_models
        self.x_axis = x_axis
        self.y_axis = y_axis

        self.setupUI()


    def setupUI(self):
        print("Graph Window Setup")
        print(self.selected_models)
        print(self.x_axis)
        print(self.y_axis)
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication

class SimulationWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, function, args=None):
        super().__init__()
        self.function = function
        self.args = args if args is not None else []

        
    def run(self):
        try:
            result = self.function(*self.args)
            self.finished.emit(f"Success: {str(result)}")
        except Exception as e:
            self.error.emit(str(e))
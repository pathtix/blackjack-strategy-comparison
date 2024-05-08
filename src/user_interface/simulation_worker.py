from PyQt6.QtCore import QThread, pyqtSignal

class SimulationWorker(QThread):
    finished = pyqtSignal(str)  # Signal to emit completion with a message
    error = pyqtSignal(str)  # Signal to handle errors as string for simplicity

    def __init__(self, function, args=None):
        super().__init__()
        self.function = function
        self.args = args if args is not None else []

    def run(self):
        try:
            result = self.function(*self.args)
            self.finished.emit(f"Success: {str(result)}")  # Send success message
        except Exception as e:
            self.error.emit(str(e))  # Send error message as string

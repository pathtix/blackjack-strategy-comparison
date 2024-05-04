from PyQt6.QtCore import QThread, pyqtSignal

class SimulationWorker(QThread):
    finished = pyqtSignal(str)  # Signal to emit upon completion with some message
    
    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        # Execute the function with the provided arguments
        result = self.function(*self.args, **self.kwargs)
        self.finished.emit(result)

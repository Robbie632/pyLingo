from PyQt5.QtCore import QRunnable

class Worker(QRunnable):

    """
    Allows func to be run on seperate thread from the gui thread
    """

    def __init__(self, func, *args, **kwargs):
        QRunnable.__init__(self)
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """
        run function on seperate thread from parent
        """
        self.func(*self.args, *self.kwargs)

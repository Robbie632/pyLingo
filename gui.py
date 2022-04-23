import sys

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow,
                             QLabel, QTextEdit, QPushButton)
from main import Interface


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow, Interface):
    def __init__(self):
        QMainWindow.__init__(self)
        Interface.__init__(self)

        self.setWindowTitle("My App")
        self.phrase = QLabel(self)

        self.phrase.setText("swedish phrase")
        self.phrase.move(10, 10)
        self.phrase.setFixedSize(500, 80)

        self.input_box = QTextEdit(self)
        self.input_box.move(10, 100)
        self.input_box.setFixedSize(500, 50)

        self.feedback = QLabel(self)
        self.feedback.setText("feedback")
        self.feedback.move(10, 150)
        self.feedback.setFixedSize(500, 80)

        control_button_height = 30
        control_button_length = 100
        horizontal_button_spacer = 10

        self.p = QPushButton(self)
        self.p.setText("peek")
        self.p.move(10, 250)
        self.p.setFixedSize(control_button_length, control_button_height)

        self.s = QPushButton(self)
        self.s.setText("skip")
        self.s.move(10+control_button_length+horizontal_button_spacer, 250)
        self.s.setFixedSize(control_button_length, control_button_height)

        self.a = QPushButton(self)
        self.a.setText("audio")
        self.a.move((2*10)+(2*control_button_length)+horizontal_button_spacer, 250)
        self.a.setFixedSize(control_button_length, control_button_height)

        self.setMinimumSize(1000, 500)

    def update_feedback(self, message: str):
        self.feedback.setText(message)

    def update_phrase(self, message: str):
        self.phrase.setText(message)

    def intro(self):
        raise NotImplementedError

    def ask(self, message: str):
        """ask the user a phrase"""
        raise NotImplementedError

    def correct(self):
        """give feedback that input was correct"""
        raise NotImplemented

    def incorrect(self):
        """give feedback that input was incorrect"""
        raise NotImplementedError

    def check_weights(self, weights: str):
        """show user probability distribution being used to
        control picking of next phrase to ask"""
        raise NotImplementedError

    def ask_load_weights(self) -> bool:
        """
        Ask user if they want ot resume using weights from previous session
        """
        raise NotImplementedError

    def play_phrase(self, filepath: str):
        raise NotImplementedError




app = QApplication([])

window = MainWindow()
window.show()

app.exec()
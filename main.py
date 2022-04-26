import json
import time
import sys
import os
from playsound import PlaysoundException
from random import choices
from game import Game
from config import Config
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow,
                             QLabel, QTextEdit, QPushButton)

from PyQt5.QtCore import Qt

class InputBox(QTextEdit):

    def __init__(self, s):
        QTextEdit.__init__(self, s)
        #self.s must already be present as an attribute in QTextEit so
        # when I know this I can reference this instead of self.s
        self.s = s

    def keyPressEvent(self, keyEvent):
        super(InputBox, self).keyPressEvent(keyEvent)
        if keyEvent.key() == Qt.Key_Return:
            self.s.on_submit()
    

class GUI(Game, QMainWindow):
    def __init__(self, syntax: list, config: Config, weights_path: str, audio_folder_path):
        self.processed_swedish = None
        self.processed_answer = None
        self.app = QApplication([])
        Game.__init__(self,  syntax, config, weights_path, audio_folder_path)
        QMainWindow.__init__(self)

        control_button_height = 30
        control_button_length = 100
        horizontal_button_spacer = 10
        control_button_vertical_placement = 300
        self.tries = 0

        self.setWindowTitle("My App")
        self.phrase = QLabel(self)

        self.phrase.setText("swedish phrase")
        self.phrase.move(10, 10)
        self.phrase.setFixedSize(500, 80)

        self.input_box = InputBox(self)
        self.input_box.move(10, 100)
        self.input_box.setFixedSize(500, 50)

        self.feedback = QLabel(self)
        self.feedback.setText("")
        self.feedback.move(10, 150)
        self.feedback.setFixedSize(500, 80)

        self.submit = QPushButton(self)
        self.submit.setText("submit")
        self.submit.move(10, 250)
        self.submit.setFixedSize(control_button_length, control_button_height)
        self.submit.clicked.connect(self.on_submit)

        self.p = QPushButton(self)
        self.p.setText("peek")
        self.p.move(10, control_button_vertical_placement)
        self.p.setFixedSize(control_button_length, control_button_height)
        self.p.clicked.connect(self.on_peek)

        self.s = QPushButton(self)
        self.s.setText("skip")
        self.s.move(10+control_button_length+horizontal_button_spacer, control_button_vertical_placement )
        self.s.setFixedSize(control_button_length, control_button_height)
        self.s.clicked.connect(self.on_skip)

        self.a = QPushButton(self)
        self.a.setText("audio")
        self.a.move((2*10)+(2*control_button_length)+horizontal_button_spacer, control_button_vertical_placement )
        self.a.setFixedSize(control_button_length, control_button_height)
        self.a.clicked.connect(self.on_audio)

        self.r = QPushButton(self)
        self.r.setText("reset")
        self.r.move((3*10)+(3*control_button_length)+horizontal_button_spacer, control_button_vertical_placement )
        self.r.setFixedSize(control_button_length, control_button_height)
        self.r.clicked.connect(self.on_reset)

        self.setMinimumSize(1000, 500)

        self.new_phrase()

    def choose_phrase(self):
        selected_syntax = choices(self.syntax, weights=self.weights)
        selected_index = self.syntax.index(selected_syntax[0])
        language1 = selected_syntax[0][0]
        language2 = selected_syntax[0][1]

        return selected_index, language1, language2

    def increase_weight(self, index: int):
        self.weights[index] += self.reward

    def decrease_weight(self, index: int):
        self.weights[index] = max(1, self.weights[index]-self.reward)

    def new_phrase(self):
        self.selected_index, self.language1, self.language2 = self.choose_phrase()
        self.update_phrase(self.language1)

    def update_feedback(self, message: str):
        self.feedback.setText(message)

    def update_phrase(self, message: str):
        self.phrase.setText(message)

    def on_peek(self):
        self.update_feedback(self.language2)

    def on_audio(self):
        audio_path = os.path.join("audio", f"{self.selected_index}.mp3")
        try:
            self.play_phrase(audio_path)
        except PlaysoundException as e:
            print(f"exception when playing audio from file {audio_path} {str(e)}")

    def on_skip(self):
        self.new_phrase()
        self.update_feedback("")

    def on_submit(self):
        answer = self.input_box.toPlainText()
        self.input_box.setText("")

        self.processed_answer = self.preprocess(answer)
        self.processed_swedish = self.preprocess(self.language2)
        
        if self.processed_answer == self.processed_swedish:
            self.correct()
            self.decrease_weight(self.selected_index)
            self.on_audio()
            self.tries = 0
            self.new_phrase()
        elif self.processed_answer != self.processed_swedish and self.tries == 3:
            self.incorrect()
            self.increase_weight(self.selected_index)
            time.sleep(1)
            self.update_feedback(self.processed_swedish)
            self.tries = 0
        elif self.processed_answer != self.processed_swedish:
            self.incorrect()
            self.increase_weight(self.selected_index)
            self.tries += 1

    def on_reset(self):
        self.reset_weights()
        self.update_feedback("weights were reset")

    def on_enter(self, qKeyEvent):
        # https://forum.qt.io/topic/103613/how-to-call-keypressevent-in-pyqt5-by-returnpressed/3
        # follow the above to implement
        print(qKeyEvent.key())
        if qKeyEvent.key() == Qt.Key_Return:
            print('Enter pressed')
        else:
            super().keyPressEvent(qKeyEvent)

    def intro(self):
        pass

    def correct(self):

        self.update_feedback("well done, correct")

    def incorrect(self):
        if self.processed_answer is not None and self.processed_swedish is not None:
            self.update_feedback(self.uppercase_incorrect_words(self.processed_answer, self.processed_swedish))

    def check_weights(self, weights: str):
        pass

    def ask_load_weights(self) -> bool:

        return True

    def reset_weights(self):

        for i in range(len(self.weights)):
            self.weights[i] = 1
        self.save_weights()

    def run(self):

        load_weights = self.ask_load_weights()
        if load_weights:
            ret = self.load_weights()

        if not load_weights or not ret:
            self.weights = len(self.syntax) * [1]

        self.show()
        self.app.exec()




if __name__ == "__main__":

    bundle_dir = Path(getattr(sys, '_MEIPASS', Path.cwd()))

    config_path = bundle_dir / 'config.json'
    phrases_path = bundle_dir / 'phrases.json'
    weights_path = bundle_dir / 'weights.json'
    audio_folder_path = bundle_dir / 'audio'

    with open(phrases_path, "r") as f:
        phrases = json.load(f)

    config = Config(config_path)

    myGame = GUI(phrases["syntax"], config, weights_path, audio_folder_path)

    myGame.run()

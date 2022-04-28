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
                             QLabel, QTextEdit, QPushButton,
                             QWidget, QHBoxLayout, QVBoxLayout, QAction)
from PyQt5.QtGui import QFont


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
    def __init__(self, phrases_category: str, config: Config):
        self.app = QApplication([])
        Game.__init__(self,  phrases_category, config)
        QMainWindow.__init__(self)

        self.load_phrases()

        w = QWidget()
        layout = QVBoxLayout()
        layout_header = QHBoxLayout()
        layout2 = QHBoxLayout()

        self.processed_swedish_with_accents = None
        self.processed_answer = None
        self.phrases_category = phrases_category
        self.load_phrases()
        self.load_weights()

        control_button_height = 30
        control_button_length = 100
        self.tries = 0

        self.setWindowTitle("pyLingo")
        self.phrase = QLabel(self)

        self.phrase.setText("")
        self.phrase.setFixedSize(500, 80)
        
        self.phrase_category_label = QLabel(self)
        self.phrase_category_label.setText(self.phrases_category)
        layout_header.addWidget(self.phrase)
        layout_header.addWidget(self.phrase_category_label)

        layout.addLayout(layout_header)

        input_font = QFont()
        input_font.setPointSize(14)
        self.input_box = InputBox(self)
        self.input_box.setFont(input_font)
        self.input_box.setFixedSize(500, 50)
        layout.addWidget(self.input_box)

        self.feedback = QLabel(self)
        self.feedback.setText("")
        layout.addWidget(self.feedback)


        self.submit = QPushButton(self)
        self.submit.setText("submit")
        self.submit.setFixedSize(control_button_length, control_button_height)
        self.submit.clicked.connect(self.on_submit)
        layout2.addWidget(self.submit)

        self.p = QPushButton(self)
        self.p.setText("peek")
        self.p.setFixedSize(control_button_length, control_button_height)
        self.p.clicked.connect(self.on_peek)
        layout2.addWidget(self.p)

        self.s = QPushButton()
        self.s.setText("skip")
        self.s.setFixedSize(control_button_length, control_button_height)
        self.s.clicked.connect(self.on_skip)
        layout2.addWidget(self.s)

        self.a = QPushButton(self)
        self.a.setText("audio")
        self.a.setFixedSize(control_button_length, control_button_height)
        self.a.clicked.connect(self.on_audio)
        layout2.addWidget(self.a)

        self.r = QPushButton(self)
        self.r.setText("reset")

        self.r.setFixedSize(control_button_length, control_button_height)
        self.r.clicked.connect(self.on_reset)
        layout2.addWidget(self.r)
        layout.addLayout(layout2)
        w.setLayout(layout)
        self.setCentralWidget(w)

        self.phrases_1_selection = QAction("conversational", self)
        self.phrases_2_selection = QAction("tutoring", self)

        self.phrases_1_selection.triggered.connect(self.on_phrase_1)
        self.phrases_2_selection.triggered.connect(self.on_phrase_2)

        menu = self.menuBar()
        categories_menu = menu.addMenu("phrase-categories")
        categories_menu.addAction(self.phrases_1_selection)
        categories_menu.addSeparator()
        categories_menu.addAction(self.phrases_2_selection)

        self.setMinimumSize(1000, 500)
        self.new_phrase()

    def on_phrase_1(self):
        self.phrases_category = self.phrases_1_selection.text()
        self.load_phrases()
        self.load_weights()
        self.new_phrase()
        self.phrase_category_label.setText(self.phrases_category)

    def on_phrase_2(self):
        self.phrases_category = self.phrases_2_selection.text()
        self.load_phrases()
        self.load_weights()
        self.new_phrase()
        self.phrase_category_label.setText(self.phrases_category)

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
        self.save_weights()
        self.selected_index, self.language1, self.language2 = self.choose_phrase()
        self.update_phrase(self.language1)

    def update_feedback(self, message: str):
        self.feedback.setText(message)

    def update_phrase(self, message: str):
        self.phrase.setText(message)

    def on_peek(self):
        self.increase_weight(self.selected_index)
        self.update_feedback(self.language2)

    def on_audio(self):
        audio_path = os.path.join("audio", self.phrases_category, f"{self.selected_index}.mp3")
        try:
            self.play_phrase(audio_path)
        except PlaysoundException as e:
            print(f"exception when playing audio from file {audio_path} {str(e)}")

    def on_skip(self):
        self.increase_weight(self.selected_index)
        self.new_phrase()
        self.update_feedback("")

    def on_submit(self):
        answer = self.input_box.toPlainText()
        self.input_box.setText("")

        self.processed_answer = self.preprocess(answer)

        self.processed_swedish_with_accents = self.preprocess(self.language2)

        self.processed_swedish_no_accents = self.replace_accents(self.processed_swedish_with_accents)

        if self.processed_answer == self.processed_swedish_no_accents:
            self.correct()
            self.decrease_weight(self.selected_index)
            self.on_audio()
            self.tries = 0
            self.new_phrase()
        elif self.processed_answer != self.processed_swedish_no_accents and self.tries == 3:
            self.incorrect()
            self.increase_weight(self.selected_index)
            time.sleep(1)
            self.update_feedback(self.processed_swedish_with_accents)
            self.tries = 0
        elif self.processed_answer != self.processed_swedish_no_accents:
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
        self.decrease_weight(self.selected_index)

    def incorrect(self):
        if self.processed_answer is not None and self.processed_swedish_with_accents is not None:
            self.update_feedback(self.uppercase_incorrect_words(self.processed_answer,
                                                                self.processed_swedish_with_accents))
            self.increase_weight(self.selected_index)

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

    config_path = 'config.json'
    phrases_category = "conversational"
    config = Config(config_path)

    myGame = GUI(phrases_category, config)

    myGame.run()

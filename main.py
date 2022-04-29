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
                             QWidget, QHBoxLayout, QVBoxLayout,
                             QAction, QStatusBar)
import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

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

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class GUI(Game, QMainWindow):
    def __init__(self, phrases_category: str, config: Config):
        self.app = QApplication([])
        Game.__init__(self,  phrases_category, config)
        QMainWindow.__init__(self)

        self.load_phrases()

        w = QWidget()
        vertical_layout = QVBoxLayout()
        layout_graph = QHBoxLayout()
        horizontal_layout = QHBoxLayout()

        self.processed_swedish_with_accents = None
        self.processed_answer = None
        self.phrases_category = phrases_category
        self.load_phrases()
        self.load_weights()

        self.phrase_category_label = QLabel(self)
        self.phrase_category_label.setText(self.phrases_category)
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.addPermanentWidget(self.phrase_category_label)
        self.phrase_category_label.setText(self.phrases_category)

        control_button_height = 30
        control_button_length = 100
        self.tries = 0

        self.setWindowTitle("pyLingo")
        self.phrase = QLabel(self)

        self.phrase.setText("")
        self.phrase.setFixedSize(500, 80)
        layout_graph.addWidget(self.phrase)

        self.graph = MplCanvas(self, width=5, height=4, dpi=100)
        layout_graph.addWidget(self.graph)
        vertical_layout.addLayout(layout_graph)

        self.update_plot()

        input_font = QFont()
        input_font.setPointSize(14)
        self.input_box = InputBox(self)
        self.input_box.setFont(input_font)
        self.input_box.setFixedSize(500, 50)
        vertical_layout.addWidget(self.input_box)

        self.feedback = QLabel(self)
        self.feedback.setText("")
        vertical_layout.addWidget(self.feedback)

        self.submit = QPushButton(self)
        self.submit.setText("submit")
        self.submit.setFixedSize(control_button_length, control_button_height)
        self.submit.clicked.connect(self.on_submit)
        horizontal_layout.addWidget(self.submit)

        self.p = QPushButton(self)
        self.p.setText("peek")
        self.p.setFixedSize(control_button_length, control_button_height)
        self.p.clicked.connect(self.on_peek)
        horizontal_layout.addWidget(self.p)

        self.s = QPushButton()
        self.s.setText("skip")
        self.s.setFixedSize(control_button_length, control_button_height)
        self.s.clicked.connect(self.on_skip)
        horizontal_layout.addWidget(self.s)

        self.a = QPushButton(self)
        self.a.setText("audio")
        self.a.setFixedSize(control_button_length, control_button_height)
        self.a.clicked.connect(self.on_audio)
        horizontal_layout.addWidget(self.a)

        self.r = QPushButton(self)
        self.r.setText("reset")

        self.r.setFixedSize(control_button_length, control_button_height)
        self.r.clicked.connect(self.on_reset)
        horizontal_layout.addWidget(self.r)
        vertical_layout.addLayout(horizontal_layout)
        w.setLayout(vertical_layout)
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
        self.update_plot()
        self.new_phrase()
        self.phrase_category_label.setText(self.phrases_category)

    def on_phrase_2(self):
        self.phrases_category = self.phrases_2_selection.text()
        self.load_phrases()
        self.load_weights()
        self.update_plot()
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
        self.save_weights()
        self.update_plot()
        self.update_feedback(self.language2)

    def on_audio(self):
        audio_path = os.path.join("assets", self.phrases_category, "audio", f"{self.selected_index}.mp3")
        try:
            self.play_phrase(audio_path)
        except PlaysoundException as e:
            print(f"exception when playing audio from file {audio_path} {str(e)}")

    def on_skip(self):
        self.increase_weight(self.selected_index)
        self.save_weights()
        self.update_plot()
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
            self.on_audio()
            self.tries = 0
            self.new_phrase()
        elif self.processed_answer != self.processed_swedish_no_accents and self.tries == 3:
            self.incorrect()
            time.sleep(1)
            self.update_feedback(self.processed_swedish_with_accents)
            self.tries = 0
        elif self.processed_answer != self.processed_swedish_no_accents:
            self.incorrect()
            self.tries += 1

    def on_reset(self):
        self.reset_weights()
        self.update_plot()
        self.update_feedback("weights were reset")

    def intro(self):
        pass

    def correct(self):
        self.update_feedback("well done, correct")
        self.decrease_weight(self.selected_index)
        self.update_plot()
        self.save_weights()

    def incorrect(self):
        if self.processed_answer is not None and self.processed_swedish_with_accents is not None:
            self.update_feedback(self.uppercase_incorrect_words(self.processed_answer,
                                                                self.processed_swedish_with_accents))
            self.increase_weight(self.selected_index)
            self.save_weights()
            self.update_plot()


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

    def update_plot(self):

        """
        Updates graph showing wieghts
        """
        self.graph.axes.clear()
        self.graph.axes.plot(range(len(self.weights)), self.weights, color ="black")
        y_positions = [1, 3, 5]

        self.graph.axes.barh(y=y_positions,
                             width=len(self.weights),
                             align="edge",
                             height=2,
                             color=[[0, 1, 0],
                                    [0.98823529, 0.85, 0.01],
                                    [1, 0, 0]])
        self.graph.axes.axis("off")
        self.graph.draw()


if __name__ == "__main__":
    config_path = 'config.json'
    phrases_category = "conversational"
    config = Config(config_path)

    myGame = GUI(phrases_category, config)

    myGame.run()

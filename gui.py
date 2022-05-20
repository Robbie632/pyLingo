import os
from random import choices
from typing import List, Tuple
import matplotlib
from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtGui import QFont, QIcon, QBrush, QPen, QColor
from PyQt5.QtWidgets import (QApplication, QMainWindow,
                             QLabel, QTextEdit, QPushButton,
                             QWidget, QHBoxLayout, QVBoxLayout,
                             QAction, QStatusBar, QMessageBox, QGraphicsScene,
                             QGraphicsEllipseItem, QGraphicsView)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from config import Config
from game import Game
from threads import Worker#
import json

matplotlib.use('Qt5Agg')

class AddPhraseWindow(QWidget):
    """
    Window for adding new phrase
    """
    def __init__(self, main_window, category):
        super().__init__()
        self.main_window = main_window
        self.category = category
        layout = QVBoxLayout()
        info = QLabel("Add a new line for each phrase, seperate lines with *")
        self.setWindowTitle("pyLingo-phrase addition")
        self.input_box_1 = QTextEdit()
        self.input_box_2 = QTextEdit()
        self.input_box_1.setFixedSize(600, 200)
        self.input_box_2.setFixedSize(600, 200)

        self.submit = QPushButton(self)
        self.submit.setText("submit")
        self.submit.setFixedSize(100, 30)
        self.submit.clicked.connect(self.on_submit)

        self.text1 = QLabel("known phrase(s)")
        self.text2 = QLabel("new language phrase(s)")
        layout.addWidget(info)
        layout.addWidget(self.text1)
        layout.addWidget(self.input_box_1)
        layout.addSpacing(50)
        layout.addWidget(self.text2)
        layout.addWidget(self.input_box_2)
        layout.addSpacing(25)
        layout.addWidget(self.submit)
        self.setFixedSize(800, 800)
        self.setLayout(layout)

    def on_submit(self) -> None:

        feedback = QMessageBox()

        syntax = self.load_phrases(self.category)
        mother_tongue_phrases = self.input_box_1.toPlainText().split("*")
        new_language_phrases = self.input_box_2.toPlainText().split("*")

        if len(mother_tongue_phrases) != len(new_language_phrases):
            feedback.setText("please enter the same number of phrases in each box")
        elif mother_tongue_phrases[0] == "" and len(mother_tongue_phrases) == 1:
            feedback.setText("Please enter some text before submitting")
        else:
            for mt, nl in zip(mother_tongue_phrases, new_language_phrases):
                syntax["syntax"].append([self.main_window.preprocess(mt), self.main_window.preprocess(nl)])
            self.write_phrases(self.category, syntax)
            self.input_box_1.clear()
            self.input_box_2.clear()
            feedback.setText(f"you have added a phrase pair to category: {self.category}")

        feedback.exec()

    def load_phrases(self, category: str) -> dict:
        path = os.path.join("assets", category, "phrases.json")

        with open(path, "r") as f:
            syntax = json.load(f)
        return syntax

    def write_phrases(self, category: str, syntax: dict) -> list:
        path = os.path.join("assets", category, "phrases.json")

        with open(path, "w") as f:
            json.dump(syntax, f, indent=4)


class InputBox(QTextEdit):

    def __init__(self, s):
        QTextEdit.__init__(self, s)
        # self.s must already be present as an attribute in QTextEit so
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
        Game.__init__(self, phrases_category, config)
        QMainWindow.__init__(self)

        self.sound_thread = QThreadPool()

        self.load_phrases()

        w = QWidget()
        vertical_layout = QVBoxLayout()
        layout_graph = QHBoxLayout()
        horizontal_layout = QHBoxLayout()

        self.processed_swedish_with_accents = None
        self.processed_answer = None
        self.processed_swedish_no_accents = None
        self.phrases_category = phrases_category
        self.load_phrases()
        self.load_weights()

        self.phrase_category_label = QLabel(self)
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.addPermanentWidget(self.phrase_category_label)
        self.phrase_category_label.setText(f"category: {self.phrases_category}")

        control_button_height = 30
        control_button_length = 100
        self.tries = 0

        self.setWindowTitle("pyLingo-Home")
        self.phrase = QLabel(self)

        self.phrase.setText("")
        self.phrase.setFixedSize(500, 80)
        self.set_font_size(self.phrase)
        layout_graph.addWidget(self.phrase)

        self.graphics_height = 200
        self.bullseye_scene = QGraphicsScene(0, 0, self.graphics_height, self.graphics_height)

        bulllseye_fills = [(255, 255, 255), (41, 39, 40), (45, 104, 181), (201, 44, 99), (235, 235, 9)]
        self.bullseye_radius = 90
        bullseye_radii = [self.bullseye_radius, 70, 50, 30, 10]

        self.bullseye_scene = self.create_bullseye(self.bullseye_scene, bulllseye_fills, bullseye_radii,
                                                   self.graphics_height)

        view = QGraphicsView(self.bullseye_scene)
        view.show()
        layout_graph.addWidget(view)
        vertical_layout.addLayout(layout_graph)

        self.update_graphic()

        self.input_box = InputBox(self)
        self.set_font_size(self.input_box)
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

        horizontal_layout.addSpacing(200)

        self.p = QPushButton(self)
        self.p.setIcon(QIcon('images/peek.png'))
        self.p.setToolTip("see translation")
        self.p.setFixedSize(control_button_length, control_button_height)
        self.p.clicked.connect(self.on_peek)
        horizontal_layout.addWidget(self.p)

        self.s = QPushButton()
        self.s.setIcon(QIcon('images/skip.png'))
        self.s.setToolTip("skip phrase")
        self.s.setFixedSize(control_button_length, control_button_height)
        self.s.clicked.connect(self.on_skip)
        horizontal_layout.addWidget(self.s)

        self.a = QPushButton(self)
        self.a.setIcon(QIcon('images/audio.png'))
        self.a.setToolTip("listen to phrase")
        self.a.setFixedSize(control_button_length, control_button_height)
        self.a.clicked.connect(self.on_audio)
        horizontal_layout.addWidget(self.a)

        vertical_layout.addLayout(horizontal_layout)
        w.setLayout(vertical_layout)
        self.setCentralWidget(w)

        menu = self.menuBar()
        categories_menu = menu.addMenu("Categories")
        settings_menu = menu.addMenu("Settings")

        for category in self.config.params["phrase-categories"]:
            action = QAction(category, self)
            action.triggered.connect(self.on_category_selection)
            categories_menu.addAction(action)
            categories_menu.addSeparator()

        font1 = QAction("Font: +", self)
        font2 = QAction("Font: -", self)
        reset_weights = QAction("Reset weights", self)
        add_phrases = QAction("Add phrase(s)", self)

        font1.triggered.connect(self.on_increase_font)
        font2.triggered.connect(self.on_decrease_font)
        reset_weights.triggered.connect(self.on_reset)
        add_phrases.triggered.connect(self.on_add_phrase)

        settings_menu.addAction(font1)
        settings_menu.addSeparator()
        settings_menu.addAction(font2)
        settings_menu.addSeparator()
        settings_menu.addAction(reset_weights)
        settings_menu.addSeparator()
        add_phrase = settings_menu.addMenu("Add phrase")

        for category in self.config.params["phrase-categories"]:
            action = QAction(category, self)
            action.triggered.connect(self.on_add_phrase)
            add_phrase.addAction(action)
            add_phrase.addSeparator()

        self.popup = QMessageBox()

        self.setFixedSize(1000, 500)
        self.initialise_category()
        self.new_phrase()

    def create_bullseye(self,
                        scene: QGraphicsScene,
                        fills: List[tuple],
                        radii: List[int],
                        graphics_height: int) -> QGraphicsScene:

        for f, r in zip(fills, radii):
            b = QBrush(QColor(*f))
            g = QGraphicsEllipseItem((graphics_height/2)-r, (graphics_height/2)-r, 2*r, 2*r)
            g.setBrush(b)
            g.setPen(QPen(QColor(0, 0, 0)))
            scene.addItem(g)
        return scene

    def plot_on_bullseye(self,
                         scene: QGraphicsScene,
                         x: int,
                         y: int,
                         graphics_height: int):

        b = QBrush(QColor(255, 255, 255))
        g = QGraphicsEllipseItem(x+(graphics_height/2), y + (graphics_height/2), 3, 3)

        g.setBrush(b)
        scene.addItem(g)
        return g


    def on_increase_font(self):

        new_size = self.config.params["aesthetics"]["font-size"] + 1
        self.config.params["aesthetics"]["font-size"] = new_size
        self.config.write_to_file()
        self.set_font_size(self.input_box)
        self.set_font_size(self.phrase)
        self.set_font_size(self.feedback)

    def update_popup_text(self, message: str):
        self.popup.setText(message)

    def on_decrease_font(self):
        new_size = self.config.params["aesthetics"]["font-size"] - 1
        self.config.params["aesthetics"]["font-size"] = new_size
        self.config.write_to_file()
        self.set_font_size(self.input_box)
        self.set_font_size(self.phrase)
        self.set_font_size(self.feedback)

    def on_category_selection(self):
        self.phrases_category = self.sender().text()
        self.initialise_category()
        self.update_popup_text(f"changed category to: {str(self.phrases_category)}")
        self.popup.exec()

    def on_add_phrase(self):
        print("on_add_phrase()")
        selected_category = self.sender().text()

        # make new window with two text boxes, one for mother tongue, other for new language
        # add phrases to list then add to self.syntax then write self.syntax to file
        self.new_phrase_window = AddPhraseWindow(self, selected_category)
        self.new_phrase_window.show()

    def set_font_size(self, widget):

        """
        sets font size of widget
        """
        font = QFont()

        font.setPointSize(self.config.params["aesthetics"]["font-size"])
        try:
            widget.setFont(font)
        except AttributeError as e:
            print(f"couldnt set font type for {str(widget)}")


    def initialise_category(self):
        """
        loads phrases and weights,
        checks weights are as expected given the phrases
        updates graphics
        """
        self.load_phrases()
        load_weights = self.load_weights()
        if not load_weights or len(self.weights) != len(self.syntax):
            self.reset_weights()
        self.update_graphic()
        self.new_phrase()
        self.phrase_category_label.setText(f"category: {self.phrases_category}")

    def increase_weight(self, index: int):
        self.weights[index] += self.reward

    def decrease_weight(self, index: int):
        self.weights[index] = max(1, self.weights[index] - self.reward)

    def update_feedback(self, message: str):
        self.feedback.setText(message)

    def update_phrase(self, message: str):
        self.phrase.setText(message)

    def update_input(self, message: str):
        self.input_box.setText(message)

    def on_peek(self):
        self.increase_weight(self.selected_index)
        self.save_weights()
        self.update_graphic()
        self.update_feedback(self.language2)

    def on_audio(self):
        """
        Uses current phrase index and searches relevant audio folde for matching file,
        this method is required because the file ending is unkown
        """
        number_file = self.selected_index
        audio_file = None

        audio_folder = os.path.join("assets", self.phrases_category, "audio")
        if os.path.isdir(audio_folder):
            relevant_audio_files = os.listdir(audio_folder)
            for f in relevant_audio_files:
                if str(number_file) == f.split(".")[0]:
                    audio_file = f
                    break
            if audio_file is None:
                audio_path = os.path.join(audio_folder, f"{str(number_file)}.mp3")
                ret = self.get_external_audio(audio_path, self.language2)
                if not ret:
                    return None
            else:
                audio_path = os.path.join(audio_folder, audio_file)
            # run function on seperate thread from gui thread
            worker = Worker(self.play_phrase, audio_path)
            self.sound_thread.start(worker)
        else:
            return None

    def on_skip(self):
        self.update_input("")
        self.increase_weight(self.selected_index)
        self.save_weights()
        self.update_graphic()
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
        elif self.processed_answer != self.processed_swedish_no_accents:
            self.incorrect()
            self.tries += 1

    def on_reset(self):
        self.reset_weights()
        self.update_graphic()
        self.update_popup_text("weights were reset")
        self.popup.exec()

    def intro(self):
        pass

    def correct(self):
        self.update_feedback("well done, correct")
        self.decrease_weight(self.selected_index)
        self.update_graphic()
        self.save_weights()

    def incorrect(self):
        if self.processed_answer is not None and self.processed_swedish_with_accents is not None:
            self.update_feedback(self.uppercase_incorrect_words(self.processed_answer,
                                                                self.processed_swedish_with_accents))
            self.increase_weight(self.selected_index)
            self.save_weights()
            self.update_graphic()

    def check_weights(self, weights: str):
        pass

    def ask_load_weights(self) -> bool:

        return True

    def reset_weights(self):

        self.weights = len(self.syntax) * [1]
        self.save_weights()

    def run(self):

        ret = self.load_weights()
        if not ret:
            self.reset_weights()
        self.show()
        self.app.exec()

    def update_graphic(self):

        """
        Updates graphic showing wieghts
        """

        # clear old bullseye

        for weight_index in range(len(self.weights)):
            _coords = self.polar_coordinate_to_cartesian(len(self.weights),
                                               weight_index,
                                               self.weights[weight_index],
                                               10,
                                               self.bullseye_radius)
            self.plot_on_bullseye(self.bullseye_scene, _coords[0], _coords[1], self.graphics_height)

if __name__ == "__main__":

    config_path = 'config.json'
    phrases_category = "conversational"
    config = Config(config_path)

    myGame = GUI(phrases_category, config)

    myGame.run()

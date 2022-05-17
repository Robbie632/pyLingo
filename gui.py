import os
from random import choices

import matplotlib
from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow,
                             QLabel, QTextEdit, QPushButton,
                             QWidget, QHBoxLayout, QVBoxLayout,
                             QAction, QStatusBar, QMessageBox)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from config import Config
from game import Game
from threads import Worker

matplotlib.use('Qt5Agg')

class AnotherWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()
        self.setWindowTitle("phrase addition")
        self.input_box_1 = QTextEdit()
        self.input_box_2 = QTextEdit()
        self.input_box_1.setFixedSize(500, 50)
        self.input_box_2.setFixedSize(500, 50)

        self.submit = QPushButton(self)
        self.submit.setText("submit")
        self.submit.clicked.connect(self.on_submit)

        self.text1 = QLabel("mother tongue phrase")
        self.text2 = QLabel("new language phrase")

        layout.addWidget(self.text1)
        layout.addWidget(self.input_box_1)
        layout.addSpacing(50)
        layout.addWidget(self.text2)
        layout.addWidget(self.input_box_2)
        layout.addSpacing(25)
        layout.addWidget(self.submit)
        self.setFixedSize(800, 400)
        self.setLayout(layout)

    def on_submit(self):
        print("clicked submit")
        # get category selected from submenu
        category = None
        # load syntax associated with selected category
        syntax = None

        #syntax.append([self.input_box_1.text(), self.input_box_2.text()])
        #self.main_window.save_phrases(category, syntax)
        self.input_box_1.clear()
        self.input_box_2.clear()
        # pop up box giving feedback


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

        self.setWindowTitle("pyLingo")
        self.phrase = QLabel(self)

        self.phrase.setText("")
        self.phrase.setFixedSize(500, 80)
        self.set_font_size(self.phrase)
        layout_graph.addWidget(self.phrase)

        self.graph = MplCanvas(self, width=3, height=2, dpi=100)
        layout_graph.addWidget(self.graph)
        vertical_layout.addLayout(layout_graph)

        self.update_plot()

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
        self.p.setFixedSize(control_button_length, control_button_height)
        self.p.clicked.connect(self.on_peek)
        horizontal_layout.addWidget(self.p)

        self.s = QPushButton()
        self.s.setIcon(QIcon('images/skip.png'))
        self.s.setFixedSize(control_button_length, control_button_height)
        self.s.clicked.connect(self.on_skip)
        horizontal_layout.addWidget(self.s)

        self.a = QPushButton(self)
        self.a.setIcon(QIcon('images/audio.png'))
        self.a.setFixedSize(control_button_length, control_button_height)
        self.a.clicked.connect(self.on_audio)
        horizontal_layout.addWidget(self.a)

        vertical_layout.addLayout(horizontal_layout)
        w.setLayout(vertical_layout)
        self.setCentralWidget(w)

        menu = self.menuBar()
        categories_menu = menu.addMenu("categories")
        settings_menu = menu.addMenu("")

        settings_menu.setIcon(QIcon('images/settings.png'))

        for category in self.config.params["phrase-categories"]:
            action = QAction(category, self)
            action.triggered.connect(self.on_category_selection)
            categories_menu.addAction(action)
            categories_menu.addSeparator()

        font1 = QAction("font: +", self)
        font2 = QAction("font: -", self)
        reset_weights = QAction("reset weights", self)
        add_phrases = QAction("Add phrase", self)

        font1.triggered.connect(self.on_increase_font)
        font2.triggered.connect(self.on_decrease_font)
        reset_weights.triggered.connect(self.on_reset)
        add_phrases.triggered.connect(self.on_add_phrase)

        settings_menu.addAction(font1)
        settings_menu.addAction(font2)
        settings_menu.addAction(reset_weights)
        add_phrase = settings_menu.addMenu("Add phrase")

        for category in self.config.params["phrase-categories"]:
            action = QAction(category, self)
            action.triggered.connect(self.on_add_phrase)
            add_phrase.addAction(action)

        self.popup = QMessageBox()

        self.setFixedSize(1000, 500)
        self.initialise_category()
        self.new_phrase()

    def on_increase_font(self):

        new_size = self.config.params["aesthetics"]["font-size"] + 1
        self.config.params["aesthetics"]["font-size"] = new_size
        self.config.write_to_file()
        self.set_font_size(self.input_box)
        self.set_font_size(self.phrase)

    def update_popup_text(self, message: str):
        self.popup.setText(message)

    def on_decrease_font(self):
        new_size = self.config.params["aesthetics"]["font-size"] - 1
        self.config.params["aesthetics"]["font-size"] = new_size
        self.config.write_to_file()
        self.set_font_size(self.input_box)
        self.set_font_size(self.phrase)

    def on_category_selection(self):
        self.phrases_category = self.sender().text()
        self.initialise_category()
        self.update_popup_text(f"changed category to: {str(self.phrases_category)}")
        self.popup.exec()

    def on_add_phrase(self):
        print("on_add_phrase()")
        print(self.sender().text())

        # make new window with two text boxes, one for mother tongue, other for new language
        # add phrases to list then add to self.syntax then write self.syntax to file
        self.new_phrase_window = AnotherWindow(self)
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
        self.update_plot()
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
        self.update_plot()
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
        elif self.processed_answer != self.processed_swedish_no_accents:
            self.incorrect()
            self.tries += 1

    def on_reset(self):
        self.reset_weights()
        self.update_plot()
        self.update_popup_text("weights were reset")
        self.popup.exec()

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

        self.weights = len(self.syntax) * [1]
        self.save_weights()

    def run(self):

        ret = self.load_weights()
        if not ret:
            self.reset_weights()
        self.show()
        self.app.exec()

    def update_plot(self):

        """
        Updates graph showing wieghts
        """

        self.graph.axes.clear()
        self.graph.axes.plot(range(len(self.weights)), self.weights, color="black")

        graph_config = self.config.params["graph"]
        y_positions = graph_config["bar-positions"]
        bar_colours = graph_config["bar-colours"]
        show_axis = graph_config["show-axis"]

        self.graph.axes.barh(y=y_positions,
                             width=len(self.weights),
                             align="edge",
                             height=2,
                             color=bar_colours)
        if not show_axis:
            self.graph.axes.axis("off")
        self.graph.draw()


if __name__ == "__main__":
    config_path = 'config.json'
    phrases_category = "conversational"
    config = Config(config_path)

    myGame = GUI(phrases_category, config)

    myGame.run()

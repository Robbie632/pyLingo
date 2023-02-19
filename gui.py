import os
from abc import ABC
from typing import List
import matplotlib
from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtGui import QFont, QIcon, QBrush, QPen, QColor
from PyQt5.QtWidgets import (QApplication, QMainWindow,
                             QLabel, QTextEdit, QPushButton,
                             QWidget, QHBoxLayout, QVBoxLayout,
                             QAction, QStatusBar, QMessageBox, QGraphicsScene,
                             QGraphicsEllipseItem, QGraphicsView, )

from add_content.add_phrases import AddPhraseWindow
from add_content.add_category import AddCategoryWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from config import Config
from game import Game
from threads import Worker

matplotlib.use('Qt5Agg')


class InputBox(QTextEdit):
    """
    class conteolling the input box
    """
    def __init__(self, s):
        QTextEdit.__init__(self, s)
        # self.s must already be present as an attribute in QTextEit so
        # when I know this I can reference this instead of self.s
        self.s = s

    def keyPressEvent(self, keyEvent):
        """
        Method executed when key pressed
        Parameters
        ----------
        keyEvent

        """
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

        self.bullseye_items = []
        self.bullseye_scene = self.create_bullseye(self.bullseye_scene, bulllseye_fills, bullseye_radii,
                                                   self.graphics_height)
        view = QGraphicsView(self.bullseye_scene)
        view.show()
        layout_graph.addWidget(view)
        vertical_layout.addLayout(layout_graph)

        self.feedback = QLabel(self)
        self.feedback.setText("")
        vertical_layout.addWidget(self.feedback)
        self.input_box = InputBox(self)
        self.set_font_size(self.input_box)
        self.input_box.setFixedSize(500, 50)
        vertical_layout.addWidget(self.input_box)
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
        add_category = QAction("Add Category", self)

        font1.triggered.connect(self.on_increase_font)
        font2.triggered.connect(self.on_decrease_font)
        reset_weights.triggered.connect(self.on_reset)
        add_phrases.triggered.connect(self.on_add_phrase)
        add_category.triggered.connect(self.on_add_category)

        settings_menu.addAction(font1)
        settings_menu.addSeparator()
        settings_menu.addAction(font2)
        settings_menu.addSeparator()
        settings_menu.addAction(reset_weights)
        settings_menu.addSeparator()
        add_phrase = settings_menu.addMenu("Add phrase")
        settings_menu.addSeparator()
        settings_menu.addAction(add_category)

        for category in self.config.params["phrase-categories"]:
            action = QAction(category, self)
            action.triggered.connect(self.on_add_phrase)
            add_phrase.addAction(action)
            add_phrase.addSeparator()

        self.popup = QMessageBox()

        self.setFixedSize(1000, 500)
        self.initialise_category()
        self.new_phrase()
        self.key_press_num = 0

    def reset_config(self):
        print(
            "implement resetting of config and call when user adds new category so ne content is immediately available")

    def keyPressEvent(self, event):
        # if event.key() == Qt.Key_Space:
        #     self.test_method()
        if event.key() == 80:
            self.test_method()

    def test_method(self):
        w = QWidget()

        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.winId())
        screenshot.save(f"{self.key_press_num}_screenshot.png", "png")
        self.key_press_num += 1
        w.close()

    @staticmethod
    def create_bullseye(scene: QGraphicsScene,
                        fills: List[tuple],
                        radii: List[int],
                        graphics_height: int) -> QGraphicsScene:
        """
        Create bullseye graphic
        Parameters
        ----------
        scene: graphics scene
        fills: list of tuples of length 3 with colour values for consentric rings of bullseye
        radii: list of radii for concentric ring sof bullseye
        graphics_height: height of the graphic

        Returns
        -------

        """
        for f, r in zip(fills, radii):
            b = QBrush(QColor(*f))
            g = QGraphicsEllipseItem((graphics_height / 2) - r, (graphics_height / 2) - r, 2 * r, 2 * r)
            g.setBrush(b)
            g.setPen(QPen(QColor(0, 0, 0)))
            scene.addItem(g)

        return scene

    def initialise_bullseye_coords(self,
                                   coords: List[List[int]],
                                   graphics_height: int):
        """
        Initialise the pointson the bullseye graphic
        Parameters
        ----------
        coords: list of corrdinates of points
        graphics_height: height of graphic
        """
        for i in self.bullseye_items:
            self.bullseye_scene.removeItem(i)

        self.bullseye_items = []
        for c in coords:
            b = QBrush(QColor(255, 255, 255))

            g = QGraphicsEllipseItem(c[0] + (graphics_height / 2) - 2.5, c[1] + (graphics_height / 2) - 2.5, 5, 5)

            g.setBrush(b)

            self.bullseye_items.append(g)
            self.bullseye_scene.addItem(g)

    def update_bullseye_coords(self,
                               coords: List[List[int]]
                               ):
        """
        Updates point son bullseye graphic
        Parameters
        ----------
        coordsL list of new coordinates
        """
        for c, item in zip(coords, self.bullseye_items):
            item.setPos(c[0], c[1])

    def on_increase_font(self):
        """
        Increases text font of app
        """
        new_size = self.config.params["aesthetics"]["font-size"] + 1
        self.config.params["aesthetics"]["font-size"] = new_size
        self.config.write_to_file()
        self.set_font_size(self.input_box)
        self.set_font_size(self.phrase)
        self.set_font_size(self.feedback)

    def update_popup_text(self, message: str):
        """
        pdates text on current pop up window
        Parameters
        ----------
        message: message to be shown
        """
        self.popup.setText(message)

    def on_decrease_font(self):
        """
        Decreases text font size of app
        -------

        """
        new_size = self.config.params["aesthetics"]["font-size"] - 1
        self.config.params["aesthetics"]["font-size"] = new_size
        self.config.write_to_file()
        self.set_font_size(self.input_box)
        self.set_font_size(self.phrase)
        self.set_font_size(self.feedback)

    def on_category_selection(self):
        """
        Method executed when category selected
        """
        self.phrases_category = self.sender().text()
        self.initialise_category()
        self.update_popup_text(f"changed category to: {str(self.phrases_category)}")
        self.popup.exec()

    def on_add_phrase(self):
        """
        Method executed when phrase added
        """
        print("on_add_phrase()")
        selected_category = self.sender().text()

        # make new window with two text boxes, one for mother tongue, other for new language
        # add phrases to list then add to self.syntax then write self.syntax to file
        self.new_phrase_window = AddPhraseWindow(self, selected_category)
        self.new_phrase_window.show()

    def on_add_category(self):
        """
        Method executed when new category added,
        """

        self.new_category_window = AddCategoryWindow(self)
        self.new_category_window.show()

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
        self.reset_graphic()
        self.new_phrase()
        self.phrase_category_label.setText(f"category: {self.phrases_category}")

    def increase_weight(self, index: int):
        """
        Increase weight of specific phrase
        Parameters
        ----------
        index; index of phrase
        """
        self.weights[index] += self.reward

    def decrease_weight(self, index: int):
        """
        Decrease weight of specific phrase
        Parameters
        ----------
        index; index of phrase
        """
        self.weights[index] = max(1, self.weights[index] - self.reward)

    def update_feedback(self, message: str, bold: bool = False, color: str="black"):
        """
        Updates text in feedback
        Parameters
        ----------
        message: message to display
        bold: whether the message should be bold or not
        color: color of text
        """
        self.feedback.setTextFormat(Qt.RichText)
        if color not in ["green", "red", "black"]:
            raise ValueError(f"trying to set text to unavailable color {color}")
        color_string = f"style=color:{color};"
        if bold:
            tag_name = "b"
        else:
            tag_name = "a"
        message = f"<{tag_name} {color_string}>{message}</{tag_name}>"
        self.feedback.setText(message)



    def update_phrase(self, message: str):
        """
        Updates phrase being tested
        Parameters
        ----------
        message: text to display
        """
        self.phrase.setText(message)

    def update_input(self, message: str):
        """
        Updates input box with text
        Parameters
        ----------
        message: text to display in input box
        """
        self.input_box.setText(message)

    def on_peek(self):
        """
        Method executed when user clicks peek button
        """
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
        """
        Method executed when user skips phrase being tested
        """
        self.update_input("")
        self.increase_weight(self.selected_index)
        self.save_weights()
        self.update_graphic()
        self.new_phrase()
        self.update_feedback("")

    def on_submit(self):
        """
        Method executed when user submits answer in input box
        """
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
        self.reset_graphic()
        self.update_popup_text("weights were reset")
        self.popup.exec()

    def intro(self):
        pass

    def correct(self):
        self.update_feedback(f"{self.phrase.text()}: {self.processed_swedish_with_accents}", bold=True, color="green")
        self.decrease_weight(self.selected_index)
        self.update_graphic()
        self.save_weights()

    def incorrect(self):
        if self.processed_answer is not None and self.processed_swedish_with_accents is not None:
            self.update_feedback(self.uppercase_incorrect_words(self.processed_answer,
                                                                self.processed_swedish_with_accents), color="red")
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

    def reset_graphic(self):
        coords = self.get_bullseye_coords()
        self.initialise_bullseye_coords(coords, self.graphics_height)

    def update_graphic(self):

        """
        Updates graphic showing wieghts
        """
        coords = self.get_bullseye_coords()
        self.update_bullseye_coords(coords)

    def get_bullseye_coords(self):

        coords = []
        for weight_index in range(len(self.weights)):
            _coords = self.polar_coordinate_to_cartesian(len(self.weights),
                                                         weight_index,
                                                         self.weights[weight_index],
                                                         10,
                                                         1,
                                                         self.bullseye_radius)
            coords.append(_coords)
        return coords


if __name__ == "__main__":
    config_path = 'config.json'
    phrases_category = "conversational"
    config = Config(config_path)

    myGame = GUI(phrases_category, config)

    myGame.run()

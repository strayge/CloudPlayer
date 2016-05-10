import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from controller import Controller
from qt_styles import *


class QMouseSlider(QSlider):
    def mousePressEvent(self, event):
        self.setValue(QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), event.x(), self.width()))

    def mouseMoveEvent(self, event):
        self.setValue(QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), event.x(), self.width()))


class QTabWidgetWithAdd(QTabWidget):
    def __init__(self):
        QTabWidget.__init__(self)
        self._action_add_tab = None
        self._build_tabs()

    def _build_tabs(self):
        self.setUpdatesEnabled(True)
        self.insertTab(0, QWidget(), '+')
        self.currentChanged.connect(self._new_tab_clicked)

    def _new_tab_clicked(self, index):
        if index == self.count() - 1:
            if self._action_add_tab:
                self._action_add_tab()
            else:
                self.insertTab(index, QWidget(), "___ %d" % (index + 1))
            self.setCurrentIndex(index)

    def addTab(self, widget, *__args):
        self.insertTab(self.count() - 1, widget, *__args)
        self.setCurrentIndex(self.count() - 2)

    def setAddTabAction(self, action):
        self._action_add_tab = action


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        frame = QFrame(self)

        self.controller = Controller(self)

        self.setCentralWidget(frame)
        self.setWindowTitle('CloudPlayer')

        self.playlist_status = QLabel()

        self.track_position = QSlider(Qt.Horizontal)
        self.track_position.setStyleSheet(qslider_stylesheet)
        self.track_position.sliderReleased.connect(self.controller.change_track_position)

        self.volume = QMouseSlider(Qt.Horizontal)
        self.volume.setMinimum(0)
        self.volume.setMaximum(100)
        self.volume.valueChanged.connect(self.controller.volume_changed)

        self.btn_play = QPushButton()
        self.btn_play.setText("Play")
        self.btn_play.clicked.connect(self.controller.play)

        self.btn_pause = QPushButton()
        self.btn_pause.setText("Pause")
        self.btn_pause.clicked.connect(self.controller.pause)

        self.btn_prev = QPushButton()
        self.btn_prev.setText("Prev")
        self.btn_prev.clicked.connect(self.controller.previous)

        self.btn_next = QPushButton()
        self.btn_next.setText("Next")
        self.btn_next.clicked.connect(self.controller.next)

        self.input = QLineEdit()
        self.input.returnPressed.connect(self.controller.search_tracks)

        self.btn_search_tracks = QPushButton()
        self.btn_search_tracks.setText("Search")
        self.btn_search_tracks.clicked.connect(self.controller.search_tracks)

        self.search_list = QListWidget()

        self.search_status = QLabel()

        self.btn_add_track = QPushButton()
        self.btn_add_track.setText("Add")
        self.btn_add_track.clicked.connect(self.controller.clicked_add_track)

        self.btn_add_all_track = QPushButton()
        self.btn_add_all_track.setText("Add All")
        self.btn_add_all_track.clicked.connect(self.controller.clicked_add_all_tracks)

        self.btn_remove_all_tracks = QPushButton()
        self.btn_remove_all_tracks.setText("Clear")
        self.btn_remove_all_tracks.clicked.connect(self.controller.remove_all_tracks)

        self.btn_load_playlist = QPushButton()
        self.btn_load_playlist.setText("Load")
        self.btn_load_playlist.clicked.connect(self.controller.load_playlist)

        self.btn_save_playlist = QPushButton()
        self.btn_save_playlist.setText("Save")
        self.btn_save_playlist.clicked.connect(self.controller.save_playlist)

        self.tabs = QTabWidgetWithAdd()
        self.tabs.setAddTabAction(self.tab_add)
        self.tabs.tabBarDoubleClicked.connect(self.tab_close)
        self.tab_add()

        self.layout_left_topbuttons = QHBoxLayout()
        self.layout_left_topbuttons.addWidget(self.btn_play)
        self.layout_left_topbuttons.addWidget(self.btn_pause)
        self.layout_left_topbuttons.addWidget(self.btn_prev)
        self.layout_left_topbuttons.addWidget(self.btn_next)

        self.layout_left_bottombuttons = QHBoxLayout()
        self.layout_left_bottombuttons.addWidget(self.btn_add_track)
        self.layout_left_bottombuttons.addWidget(self.btn_add_all_track)

        self.layout_search_input = QHBoxLayout()
        self.layout_search_input.addWidget(self.input)
        self.layout_search_input.addWidget(self.btn_search_tracks)

        self.layout_left = QVBoxLayout()
        self.layout_left.addLayout(self.layout_left_topbuttons)
        self.layout_left.addWidget(self.track_position)
        self.layout_left.addWidget(self.volume)
        self.layout_left.addLayout(self.layout_search_input)
        self.layout_left.addWidget(self.search_list)
        self.layout_left.addWidget(self.search_status)
        self.layout_left.addLayout(self.layout_left_bottombuttons)

        self.layout_right_bottombuttons = QHBoxLayout()
        self.layout_right_bottombuttons.addWidget(self.btn_remove_all_tracks)
        self.layout_right_bottombuttons.addWidget(self.btn_load_playlist)
        self.layout_right_bottombuttons.addWidget(self.btn_save_playlist)

        self.layout_right = QVBoxLayout()
        self.layout_right.addWidget(self.tabs)
        self.layout_right.addWidget(self.playlist_status)
        self.layout_right.addLayout(self.layout_right_bottombuttons)

        self.layout_main = QHBoxLayout(frame)
        self.layout_main.addLayout(self.layout_left)
        self.layout_main.addLayout(self.layout_right)

        # self.controller.add_track(sc_get_track(49746879))
        # self.controller.add_track(sc_get_track(22728013))
        # self.controller.add_track(sc_get_track(73115505))

        self.volume.setValue(80)
        self.controller.load_current_state()

    def tab_add(self):
        new_list = QListWidget()
        new_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        new_list.setContextMenuPolicy(Qt.CustomContextMenu)
        new_list.customContextMenuRequested.connect(self.list_popup)
        new_list.itemDoubleClicked.connect(self.controller.change_track)
        name = "tab %d" % self.tabs.count()
        self.tabs.addTab(new_list, name)
        self.controller.add_playlist(name)

    def tab_close(self, index):
        # change current index to previous (if last) to prevent open "+" tab
        if self.tabs.currentIndex() == self.tabs.count() - 2:
            self.tabs.setCurrentIndex(self.tabs.count() - 3)
        self.tabs.removeTab(index)
        self.controller.remove_playlist(index)

    def list_popup(self, point):
        popup = QMenu()
        popup.addAction("Remove", self.controller.remove_track)
        popup.addAction("Find similar", self.controller.search_similar)
        popup.addAction("Save", self.controller.save_track)
        current_list = self.tabs.currentWidget()
        popup.exec(current_list.mapToGlobal(point))

    def set_title(self, title=""):
        if title == '':
            title = 'CloudPlayer'
        else:
            title += ' - CloudPlayer'
        self.setWindowTitle(title)

    def closeEvent(self, event):
        self.controller.save_current_state()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())

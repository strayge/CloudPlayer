import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from cloud_api import *
from controller import Controller
from qt_styles import *

searched_tracks = []


class QMouseSlider(QSlider):
    def mousePressEvent(self, event):
        self.setValue(QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), event.x(), self.width()))

    def mouseMoveEvent(self, event):
        self.setValue(QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), event.x(), self.width()))

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        frame = QFrame(self)

        self.setCentralWidget(frame)
        self.setWindowTitle('CloudPlayer')

        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.playlist_status = QLabel()

        self.track_position = QSlider(Qt.Horizontal)
        self.track_position.setStyleSheet(qslider_stylesheet)

        self.volume = QMouseSlider(Qt.Horizontal)
        self.volume.setMinimum(0)
        self.volume.setMaximum(100)

        self.popup_track_menu = QMenu()

        self.controller = Controller(self)

        action_remove = QAction(QIcon(), 'Remove', self)
        action_remove.triggered.connect(self.controller.remove_track)
        self.popup_track_menu.addAction(action_remove)

        action_similar = QAction(QIcon(), 'Find similar', self)
        action_similar.triggered.connect(self.search_similar)
        self.popup_track_menu.addAction(action_similar)

        action_save_track = QAction(QIcon(), 'Save', self)
        action_save_track.triggered.connect(self.controller.save_track)
        self.popup_track_menu.addAction(action_save_track)

        self.list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self.list_popup)

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
        self.input.returnPressed.connect(self.search_tracks)

        self.btn_search_tracks = QPushButton()
        self.btn_search_tracks.setText("Search")
        self.btn_search_tracks.clicked.connect(self.search_tracks)

        self.search_list = QListWidget()

        self.search_status = QLabel()

        self.btn_add_track = QPushButton()
        self.btn_add_track.setText("Add")
        self.btn_add_track.clicked.connect(self.add_track)

        self.btn_add_all_track = QPushButton()
        self.btn_add_all_track.setText("Add All")
        self.btn_add_all_track.clicked.connect(self.add_all_tracks)

        self.btn_remove_all_tracks = QPushButton()
        self.btn_remove_all_tracks.setText("Clear")
        self.btn_remove_all_tracks.clicked.connect(self.controller.remove_all_tracks)

        self.btn_load_playlist = QPushButton()
        self.btn_load_playlist.setText("Load")
        self.btn_load_playlist.clicked.connect(self.controller.load_playlist)

        self.btn_save_playlist = QPushButton()
        self.btn_save_playlist.setText("Save")
        self.btn_save_playlist.clicked.connect(self.controller.save_playlist)

        self.tabs = QTabWidget()
        self.tab1 = QListWidget()
        self.tabs.addTab(self.list, "tab1")
        # self.tabs.addTab(self.tab1, "")

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

        self.controller.add_track(sc_get_track(49746879))
        self.controller.add_track(sc_get_track(22728013))
        self.controller.add_track(sc_get_track(73115505))

        self.volume.setValue(80)

    def list_popup(self, point):
        self.popup_track_menu.exec(self.list.mapToGlobal(point))

    def search_tracks(self):
        self.search_list.clear()
        tracks = sc_search_tracks(self.input.text())
        global searched_tracks
        searched_tracks = tracks
        total_duration = 0
        for track in searched_tracks:
            self.search_list.addItem(track.title)
            total_duration += track.duration
        self.search_status.setText("Founded %i tracks. Total duration %i:%02i:%02i:%02i" %
                                   (len(searched_tracks),
                                    total_duration // 86400000, total_duration // 3600000 % 24,
                                    total_duration // 60000 % 60, total_duration // 1000 % 60))

    def search_similar(self):
        self.search_list.clear()
        position = self.list.currentRow()
        track = self.controller.playlists[self.controller.active_playlist].tracks[position]

        related_tracks = track.search_related()
        global searched_tracks
        searched_tracks = related_tracks
        total_duration = 0
        for track in searched_tracks:
            self.search_list.addItem(track.title)
            total_duration += track.duration
        self.search_status.setText("Founded %i tracks. Total duration %i:%02i:%02i:%02i" %
                                   (len(searched_tracks),
                                    total_duration // 86400000, total_duration // 3600000 % 24,
                                    total_duration // 60000 % 60, total_duration // 1000 % 60))

    def add_track(self):
        position = self.search_list.currentRow()
        self.controller.add_track(searched_tracks[position])

    def add_all_tracks(self):
        for row in range(self.search_list.count()):
            self.controller.add_track(searched_tracks[row])

    def set_title(self, title=""):
        if title == '':
            title = 'CloudPlayer'
        else:
            title += ' - CloudPlayer'
        self.setWindowTitle(title)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())

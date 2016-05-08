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

        self.grid = QGridLayout(frame)
        self.setCentralWidget(frame)
        self.setWindowTitle('SoundCloud PyPlayer')

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

        # self.btn_find_similar = QPushButton()
        # self.btn_find_similar.setText("Similar")
        # self.btn_find_similar.clicked.connect(self.search_similar)
        #
        # self.btn_remove_track = QPushButton()
        # self.btn_remove_track.setText("Remove")
        # self.btn_remove_track.clicked.connect(self.player.remove_track)

        self.btn_remove_all_tracks = QPushButton()
        self.btn_remove_all_tracks.setText("Clear")
        self.btn_remove_all_tracks.clicked.connect(self.controller.remove_all_tracks)

        self.btn_load_playlist = QPushButton()
        self.btn_load_playlist.setText("Load")
        self.btn_load_playlist.clicked.connect(self.controller.load_playlist)

        self.btn_save_playlist = QPushButton()
        self.btn_save_playlist.setText("Save")
        self.btn_save_playlist.clicked.connect(self.controller.save_playlist)

        self.grid.addWidget(self.btn_play, 0, 0)
        self.grid.addWidget(self.btn_pause, 0, 1)
        self.grid.addWidget(self.btn_prev, 0, 2)
        self.grid.addWidget(self.btn_next, 0, 3)
        self.grid.addWidget(self.track_position, 1, 0, 1, 4)
        self.grid.addWidget(self.volume, 2, 0, 1, 4)
        self.grid.addWidget(self.input, 3, 0, 1, 3)
        self.grid.addWidget(self.btn_search_tracks, 3, 3, 1, 1)
        self.grid.addWidget(self.search_list, 4, 0, 1, 4)
        self.grid.addWidget(self.search_status, 5, 0, 1, 4)
        self.grid.addWidget(self.btn_add_track, 6, 0, 1, 2)
        self.grid.addWidget(self.btn_add_all_track, 6, 2, 1, 2)
        self.grid.addWidget(self.list, 0, 4, 5, 3)
        self.grid.addWidget(self.playlist_status, 5, 4, 1, 3)
        # self.grid.addWidget(self.btn_find_similar,  6, 4, 1, 1)
        # self.grid.addWidget(self.btn_remove_track,  6, 5, 1, 1)
        self.grid.addWidget(self.btn_remove_all_tracks, 6, 4, 1, 1)
        self.grid.addWidget(self.btn_load_playlist, 6, 5, 1, 1)
        self.grid.addWidget(self.btn_save_playlist, 6, 6, 1, 1)

        self.controller.add_track(sc_get_track(49746879))
        self.controller.add_track(sc_get_track(22728013))
        self.controller.add_track(sc_get_track(73115505))
        # self.player.add_track(22728013)
        # self.player.add_track(73115505)

        self.volume.setValue(80)

    # def volume_change(self, value):
    #     self.player._player.setVolume(value)

    # def track_position_changed(self, position):
    #     self.track_position.setValue(position)

    def list_popup(self, point):
        self.popup_track_menu.exec(self.list.mapToGlobal(point))

    def search_tracks(self):
        self.search_list.clear()
        tracks = sc_search_tracks(self.input.text())
        # tracks = client.get('/tracks', q=self.input.text())
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
        # track = self.player.playlist[position]

        related_tracks = track.search_related()
        # related_tracks = client.get('/tracks/%i/related' % track.id)
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())

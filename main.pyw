import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import *

from cloud_api import *
from qt_styles import *

searched_tracks = []


class QMouseSlider(QSlider):
    def mousePressEvent(self, event):
        self.setValue(QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), event.x(), self.width()))

    def mouseMoveEvent(self, event):
        self.setValue(QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), event.x(), self.width()))


class Player:
    def __init__(self, qlist, qposition, qvolume, qstatus):
        self._list = qlist
        self._track_position = qposition
        self._volume = qvolume
        self._status = qstatus

        self._volume.valueChanged.connect(self._volume_changed)

        self._player = QMediaPlayer()
        self._player.mediaStatusChanged.connect(self._player_status_changed)
        self._player.mediaChanged.connect(self._player_media_changed)
        self._player.currentMediaChanged.connect(self._player_current_media_changed)
        self._player.stateChanged.connect(self._player_state_changed)
        self._player.positionChanged.connect(self._player_position_changed)
        self._player.durationChanged.connect(self._player_duration_changed)

        # self.qplaylist = QMediaPlaylist()
        # self.qplayer.setPlaylist(self.qplaylist)
        self.playlists = []
        # todo: load saved playlists here
        self.playlists.append(Playlist())
        self.active_playlist = 0
        # self.qplaylist.currentIndexChanged.connect(self.update_list_position)
        self._list.itemDoubleClicked.connect(self.change_track)
        self._track_position.sliderReleased.connect(self.change_track_position)

    def _player_status_changed(self, status):
        print('_player_status_changed', status)
        if status in [QMediaPlayer.EndOfMedia, QMediaPlayer.InvalidMedia]:
            self.next()

    def _player_media_changed(self, media):
        print('_player_media_changed', media)

    def _player_current_media_changed(self, media):
        print('_player_current_media_changed', media)

    def _player_state_changed(self, state):
        print('_player_state_changed', state)

    def _player_duration_changed(self, duration):
        print('_player_duration_changed', duration)
        self._track_position.setMaximum(duration)

    def _player_position_changed(self, pos):
        self._track_position.setValue(pos)

    def _volume_changed(self, value):
        self._player.setVolume(value)

    def update_status(self):
        total_duration = 0
        for track in self.playlists[self.active_playlist].tracks:
            total_duration += track.duration
        self._status.setText("%i tracks. Total duration %i:%02i:%02i:%02i" %
                             (self.playlists[self.active_playlist].count(), total_duration // 86400,
                              total_duration // 3600 % 24,
                              total_duration // 60 % 60, total_duration % 60))

    def add_track(self, track):
        self.playlists[self.active_playlist].add(track)
        self._list.addItem(track.title)
        self.update_status()

    def remove_track(self):
        position = self._list.currentRow()
        if position != -1:
            self._list.takeItem(position)
            self.playlists[self.active_playlist].remove(position)
            # del(self.playlists[self.active_playlist].tracks[position])
            # self.qplaylist.removeMedia(position)
            self.update_status()

    def remove_all_tracks(self):
        self.playlists[self.active_playlist].clear()
        # self.qplaylist.clear()
        self._list.clear()
        self.update_status()

    def next(self):
        print('next')
        next_pos = self.playlists[self.active_playlist].active_track + 1
        if next_pos < self.playlists[self.active_playlist].count():
            self.playlists[self.active_playlist].active_track = next_pos
            url = self.playlists[self.active_playlist].tracks[next_pos].stream_url()
            self._player.setMedia(QMediaContent(QUrl(url)))
            self.play()

    def previous(self):
        print('previous')
        prev_pos = self.playlists[self.active_playlist].active_track - 1
        if prev_pos >= 0:
            self.playlists[self.active_playlist].active_track = prev_pos
            url = self.playlists[self.active_playlist].tracks[prev_pos].stream_url()
            self._player.setMedia(QMediaContent(QUrl(url)))
            self.play()

    def play(self):
        self._player.play()

    def pause(self):
        self._player.pause()

    def update_list_position(self, position):
        # self.status.setText(str(position))
        for i in range(self._list.count()):
            self._list.item(i).setBackground(QBrush())
        if (position >= 0) and (position <= self._list.count()):
            self._list.item(position).setBackground(QBrush(QColor('red')))

        self._list.setCurrentRow(position)

        self._track_position.setMaximum(self.playlists[self.active_playlist].tracks[position].duration)

    def change_track(self, item):
        print('change_track')
        position = self._list.currentRow()

        self.playlists[self.active_playlist].active_track = position
        print(position)
        url = self.playlists[self.active_playlist].tracks[position].stream_url()

        self._player.setMedia(QMediaContent(QUrl(url)))
        # print(self._player.media())
        # print(self._player.state())
        if self._player.state() in [QMediaPlayer.StoppedState, QMediaPlayer.PausedState]:
            self.play()

    def change_track_position(self):
        self._player.setPosition(self._track_position.value())

    def save_track(self):
        position = self._list.currentRow()
        track = self.playlist[position]
        track.save()
        # url = '%s?client_id=%s' % (track.stream_url, client_id)
        # r = requests.get(url)
        # if r.status_code == 200:
        #     filename = track.title + '.' + track.original_format
        #     f = open(filename, 'wb')
        #     for data in r.iter_content():
        #         f.write(data)
        #     f.close()

    def load_playlist(self):
        name = 'pyplayer1'
        loaded_playlist = sc_load_playlist(name)
        # todo: need load with update gui. check
        self.playlists[self.active_playlist] = loaded_playlist
        self.update_status()
        # playlists = client.get('/me/playlists')
        # for p in playlists:
        #     if p.title == name:
        #         self.playlist.clear()
        #         self.qplaylist.clear()
        #         self._list.clear()
        #         for track in p.tracks:
        #             t = soundcloud.resource.Resource(track)
        #             self.add_track(t)
        #         self.update_status()
        #     break

    def save_playlist(self):
        name = 'pyplayer1'
        sc_save_playlist(name, self.playlists[self.active_playlist])
        # tracks = []
        # for track in self.playlist:
        #     tracks.append(dict(id=track.id))
        # playlists = client.get('/me/playlists')
        # # remove all older playlists
        # for p in playlists:
        #     if p.title == name:
        #         client.delete('/playlists/%i' % p.id)
        # # save new
        # client.post('/playlists', playlist={'title': name, 'sharing': 'public', 'tracks': tracks})


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        frame = QFrame(self)

        self.grid = QGridLayout(frame)
        self.setCentralWidget(frame)
        self.setWindowTitle('SoundCloud PyPlayer')

        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # self.list.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.playlist_status = QLabel()

        self.track_position = QSlider(Qt.Horizontal)
        # self.track_position.setMinimum(0)
        # self.track_position.setMaximum(100)
        self.track_position.setStyleSheet(qslider_stylesheet)

        self.volume = QMouseSlider(Qt.Horizontal)
        # self.volume.valueChanged.connect(self.volume_change)
        self.volume.setMinimum(0)
        self.volume.setMaximum(100)

        self.player = Player(self.list, self.track_position, self.volume, self.playlist_status)

        # self.player._player.positionChanged.connect(self.track_position_changed)

        self.popup_track_menu = QMenu()

        action_remove = QAction(QIcon(), 'Remove', self)
        action_remove.triggered.connect(self.player.remove_track)
        self.popup_track_menu.addAction(action_remove)

        action_similar = QAction(QIcon(), 'Find similar', self)
        action_similar.triggered.connect(self.search_similar)
        self.popup_track_menu.addAction(action_similar)

        action_save_track = QAction(QIcon(), 'Save', self)
        action_save_track.triggered.connect(self.player.save_track)
        self.popup_track_menu.addAction(action_save_track)

        self.list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self.list_popup)

        self.btn_play = QPushButton()
        self.btn_play.setText("Play")
        self.btn_play.clicked.connect(self.player.play)

        self.btn_pause = QPushButton()
        self.btn_pause.setText("Pause")
        self.btn_pause.clicked.connect(self.player.pause)

        self.btn_prev = QPushButton()
        self.btn_prev.setText("Prev")
        self.btn_prev.clicked.connect(self.player.previous)

        self.btn_next = QPushButton()
        self.btn_next.setText("Next")
        self.btn_next.clicked.connect(self.player.next)

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
        self.btn_remove_all_tracks.clicked.connect(self.player.remove_all_tracks)

        self.btn_load_playlist = QPushButton()
        self.btn_load_playlist.setText("Load")
        self.btn_load_playlist.clicked.connect(self.player.load_playlist)

        self.btn_save_playlist = QPushButton()
        self.btn_save_playlist.setText("Save")
        self.btn_save_playlist.clicked.connect(self.player.save_playlist)

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

        self.player.add_track(sc_get_track(49746879))
        self.player.add_track(sc_get_track(22728013))
        self.player.add_track(sc_get_track(73115505))
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
        track = self.player.playlists[self.player.active_playlist].tracks[position]
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
        self.player.add_track(searched_tracks[position])

    def add_all_tracks(self):
        for row in range(self.search_list.count()):
            self.player.add_track(searched_tracks[row])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())

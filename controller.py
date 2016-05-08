from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from cloud_api import *


class Controller:
    def __init__(self, view):
        self.view = view

        self._list = view.list
        self._track_position = view.track_position
        self._volume = view.volume
        self._status = view.playlist_status

        self._volume.valueChanged.connect(self._volume_changed)

        self._player = QMediaPlayer()
        self._player.mediaStatusChanged.connect(self._player_status_changed)
        self._player.mediaChanged.connect(self._player_media_changed)
        self._player.currentMediaChanged.connect(self._player_current_media_changed)
        self._player.stateChanged.connect(self._player_state_changed)
        self._player.positionChanged.connect(self._player_position_changed)
        self._player.durationChanged.connect(self._player_duration_changed)

        self.playlists = []
        # todo: load saved playlists here
        self.playlists.append(Playlist())
        self.active_playlist = 0
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
        if self._player.state() in [QMediaPlayer.StoppedState, QMediaPlayer.PausedState]:
            self.play()

    def change_track_position(self):
        self._player.setPosition(self._track_position.value())

    def save_track(self):
        position = self._list.currentRow()
        track = self.playlist[position]
        track.save()

    def load_playlist(self):
        name = 'pyplayer1'
        loaded_playlist = sc_load_playlist(name)
        # todo: need load with update gui. check
        self.playlists[self.active_playlist] = loaded_playlist
        self.update_status()

    def save_playlist(self):
        name = 'pyplayer1'
        sc_save_playlist(name, self.playlists[self.active_playlist])

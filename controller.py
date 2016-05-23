from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from cloud_api import *


class Controller:
    def __init__(self, view, log):
        self.log = log
        self.view = view
        self._player = QMediaPlayer()
        self._player.mediaStatusChanged.connect(self._player_status_changed)
        self._player.mediaChanged.connect(self._player_media_changed)
        self._player.currentMediaChanged.connect(self._player_current_media_changed)
        self._player.stateChanged.connect(self._player_state_changed)
        self._player.positionChanged.connect(self._player_position_changed)
        self._player.durationChanged.connect(self._player_duration_changed)
        self._searched_tracks = []
        self.playlists = []
        self.active_playlist = 0
        self.last_colored_item = None

    def _player_status_changed(self, status):
        self.log.debug('_player_status_changed: %s', str(status))
        if status in [QMediaPlayer.EndOfMedia, QMediaPlayer.InvalidMedia]:
            self.next()

        if status in [QMediaPlayer.EndOfMedia, QMediaPlayer.NoMedia, QMediaPlayer.UnknownMediaStatus,
                      QMediaPlayer.InvalidMedia]:
            self.view.set_title()
        else:
            try:
                pos = self.playlists[self.active_playlist].active_track
                if pos >= 0:
                    track = self.playlists[self.active_playlist].tracks[pos]
                    self.view.set_title(track.title)
                self.update_list_position(pos)
            except IndexError:
                self.log.error('Index error in _player_status_changed')

    def _player_media_changed(self, media):
        self.log.debug('_player_media_changed: %s' % str(media))

    def _player_current_media_changed(self, media):
        self.log.debug('_player_current_media_changed: %s' % str(media))

    def _player_state_changed(self, state):
        self.log.debug('_player_state_changed: %s' % str(state))

    def _player_duration_changed(self, duration):
        self.log.debug('_player_duration_changed: %s' % str(duration))
        self.view.track_position.setMaximum(duration)

    def _player_position_changed(self, pos):
        self.view.track_position.setValue(pos)

    def volume_changed(self, value):
        self._player.setVolume(value)

    def update_status(self):
        total_duration = 0
        for track in self.playlists[self.active_playlist].tracks:
            total_duration += track.duration
        self.view.playlist_status.setText("%i tracks. Total duration %i:%02i:%02i:%02i" %
                                          (self.playlists[self.active_playlist].count(), total_duration // 86400,
                                           total_duration // 3600 % 24,
                                           total_duration // 60 % 60, total_duration % 60))

    def add_track(self, track, playlist_index=None):
        if playlist_index is None:
            playlist_index = self.view.tabs.currentIndex()
        self.playlists[playlist_index].add(track)
        self.view.tabs.widget(playlist_index).addItem(track.title)

    def remove_track(self, track_pos=None):
        if track_pos is None:
            track_pos = self.view.tabs.currentWidget().currentRow()
        if track_pos != -1:
            self.view.tabs.currentWidget().takeItem(track_pos)
            self.playlists[self.active_playlist].remove(track_pos)
            self.update_status()

    def remove_all_tracks(self):
        playlist_index = self.view.tabs.currentIndex()
        self.playlists[playlist_index].clear()
        self.view.tabs.currentWidget().clear()
        self.update_status()

    def next(self):
        self.log.debug('next')
        # if we close last tab with current track, after it ended, we stop playing
        # todo: need check, that if we close not last tab with current song, we also need stop after song ended
        if self.active_playlist >= len(self.playlists):
            return
        next_pos = self.playlists[self.active_playlist].active_track + 1
        if next_pos < self.playlists[self.active_playlist].count():
            self.playlists[self.active_playlist].active_track = next_pos
            url = self.playlists[self.active_playlist].tracks[next_pos].stream_url()
            self._player.setMedia(QMediaContent(QUrl(url)))
            self.play()

    def previous(self):
        self.log.debug('previous')
        prev_pos = self.playlists[self.active_playlist].active_track - 1
        if prev_pos >= 0:
            self.playlists[self.active_playlist].active_track = prev_pos
            url = self.playlists[self.active_playlist].tracks[prev_pos].stream_url()
            self._player.setMedia(QMediaContent(QUrl(url)))
            self.play()

    def play(self):
        self.log.debug('play')
        self._player.play()

    def pause(self):
        self.log.debug('pause')
        self._player.pause()

    def update_list_position(self, position):
        showed_list = self.view.tabs.currentWidget()
        if self.last_colored_item:
            self.last_colored_item.setBackground(QBrush())
        if (position >= 0) and (position <= showed_list.count()):
            self.last_colored_item = showed_list.item(position)
            self.last_colored_item.setBackground(QBrush(QColor('red')))

    def change_track(self):
        self.log.debug('change_track')
        playlist_index = self.view.tabs.currentIndex()
        self.active_playlist = playlist_index
        position = self.view.tabs.currentWidget().currentRow()
        self.playlists[self.active_playlist].active_track = position
        self.log.debug('position: %i' % position)
        url = self.playlists[self.active_playlist].tracks[position].stream_url()
        self._player.setMedia(QMediaContent(QUrl(url)))
        if self._player.state() in [QMediaPlayer.StoppedState, QMediaPlayer.PausedState]:
            self.play()

    def change_track_position(self):
        self._player.setPosition(self.view.track_position.value())

    def remove_dublicates(self):
        selected_playlist = self.view.tabs.currentIndex()
        playlist = self.playlists[selected_playlist]
        processed_ids = []
        position_for_removing = []
        for index in range(len(playlist.tracks)):
            if playlist.tracks[index].id in processed_ids:
                position_for_removing.append(index)
            else:
                processed_ids.append(playlist.tracks[index].id)

        self.log.debug('tracks count: %i' % len(playlist.tracks))
        counter = 0
        for index in reversed(position_for_removing):
            self.log.debug('track index for removing: %i' % index)
            self.remove_track(track_pos=index)
            counter += 1
        self.log.info('Removed %i tracks.' % counter)

    def save_track(self, playlist_pos=None, track_pos=None):
        if track_pos is None:
            track_pos = self.view.tabs.currentWidget().currentRow()
        if playlist_pos is None:
            playlist_pos = self.view.tabs.currentIndex()
        playlist = self.playlists[playlist_pos]
        track = playlist.tracks[track_pos]
        track.save()

    def download_playlist(self):
        selected_playlist = self.view.tabs.currentIndex()
        playlist = self.playlists[selected_playlist]
        for track_pos in range(playlist.count()):
            self.log.info('Saving %i/%s track...' % (track_pos+1, playlist.count()))
            self.save_track(playlist_pos=selected_playlist, track_pos=track_pos)
        self.log.info('Saving done.')

    def load_playlist(self):
        playlist_index = self.view.tabs.currentIndex()
        playlist = self.playlists[playlist_index]
        loaded_playlist = sc_load_playlist(playlist.name)
        self.remove_all_tracks()
        for track in loaded_playlist:
            self.add_track(track)
        self.update_status()

    def save_playlist(self):
        playlist_index = self.view.tabs.currentIndex()
        playlist = self.playlists[playlist_index]
        sc_save_playlist(playlist.name, playlist)

    def add_playlist(self, name):
        self.playlists.append(Playlist(name))

    def remove_playlist(self, index):
        self.log.debug('remove playlist with index = %i' % index)
        del (self.playlists[index])

    def search_tracks(self):
        self.view.search_list.clear()
        tracks = sc_search_tracks(self.view.input.text())
        self._searched_tracks = tracks
        total_duration = 0
        for track in self._searched_tracks:
            self.view.search_list.addItem(track.title)
            total_duration += track.duration
        self.view.search_status.setText("Founded %i tracks. Total duration %i:%02i:%02i:%02i" %
                                        (len(self._searched_tracks),
                                         total_duration // 86400000, total_duration // 3600000 % 24,
                                         total_duration // 60000 % 60, total_duration // 1000 % 60))

    def search_similar(self):
        self.view.search_list.clear()
        position = self.view.tabs.currentWidget().currentRow()
        track = self.playlists[self.active_playlist].tracks[position]

        related_tracks = track.search_related()
        self._searched_tracks = related_tracks
        total_duration = 0
        for track in self._searched_tracks:
            self.view.search_list.addItem(track.title)
            total_duration += track.duration
        self.view.search_status.setText("Founded %i tracks. Total duration %i:%02i:%02i:%02i" %
                                        (len(self._searched_tracks),
                                         total_duration // 86400000, total_duration // 3600000 % 24,
                                         total_duration // 60000 % 60, total_duration // 1000 % 60))

    def clicked_add_track(self):
        position = self.view.search_list.currentRow()
        self.add_track(self._searched_tracks[position])

    def clicked_add_all_tracks(self):
        for row in range(self.view.search_list.count()):
            self.add_track(self._searched_tracks[row])

    def load_current_state(self):
        if not os.path.isfile('state.pickle'):
            return
        f = open('state.pickle', 'rb')
        state = pickle.load(f)
        f.close()
        loaded_playlists = state['playlists']
        self.log.debug('loaded %i playlists.' % len(loaded_playlists))
        for i in range(len(loaded_playlists) - len(self.playlists)):
            self.view.tab_add()
        self.playlists.clear()
        index = 0
        for playlist in loaded_playlists:
            self.log.debug('playlist: %s, len: %i' % (playlist.name, len(playlist.tracks)))
            self.add_playlist(playlist.name)
            for track in playlist.tracks:
                self.add_track(track, playlist_index=index)
            index += 1
        self.log.debug(len(self.playlists))
        self.log.debug('curent tab: %i' % state['current_playlist'])
        self.view.tabs.setCurrentIndex(state['current_playlist'])
        self.log.debug('volume: %i' % state['volume'])
        self.view.volume.setValue(state['volume'])

    def save_current_state(self):
        state = dict()
        self.log.debug('playlists count: %i' % len(self.playlists))
        state['playlists'] = self.playlists
        state['current_playlist'] = self.view.tabs.currentIndex()
        state['volume'] = self.view.volume.value()
        f = open('state.pickle', 'wb')
        pickle.dump(state, f)
        f.close()

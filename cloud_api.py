from pleercom import PleerApi
import soundcloud
import pickle
import requests
import os
import json

# for pickle
from soundcloud.resource import Resource

def soundcloud_resource_getattr(self, name):
    if name == 'obj':
        return object.__getattr__(self, name)
    if name in self.obj:
        return self.obj.get(name)
    raise AttributeError
def soundcloud_resource_getstate(self):
    return dict(self.obj.items())
def soundcloud_resource_setstate(self, items):
    if not hasattr(self, 'obj'):
        self.obj = {}
    for key in items.keys():
        self.obj[key] = items[key]
Resource.__getstate__ = soundcloud_resource_getstate
Resource.__setstate__ = soundcloud_resource_setstate
Resource.__getattr__ = soundcloud_resource_getattr


SETTINGS_FILENAME = 'settings.json'
if not os.path.isfile(SETTINGS_FILENAME):
    settings_file = open(SETTINGS_FILENAME, 'w')
    settings_file.write("""{"soundcloud": {"access_token": "TOKEN",
                               "client_id": "ID",
                               "client_secret": "SECRET"},
                "pleer": {"app_id": "ID",
                          "app_key": "KEY"}
               }""")
    settings_file.close()
    print('You need set your keys in %s' % SETTINGS_FILENAME)
    exit()

settings_file = open(SETTINGS_FILENAME, 'r')
settings = json.load(settings_file)
settings_file.close()

soundcloud_access_token = settings['soundcloud']['access_token']
soundcloud_client_id = settings['soundcloud']['client_id']
soundcloud_client_secret = settings['soundcloud']['client_secret']
pleer_app_id = settings['pleer']['app_id']
pleer_app_key = settings['pleer']['app_key']

_pleer = PleerApi(pleer_app_id, pleer_app_key)
_client = soundcloud.Client(client_id=soundcloud_client_id,
                                 client_secret=soundcloud_client_secret,
                                 access_token=soundcloud_access_token)


class Playlist:
    def __init__(self, name='Untitled'):
        self.tracks = []
        self.name = name
        self.active_track = 0

    def count(self):
        return len(self.tracks)

    def clear(self):
        self.tracks = []

    def add(self, track):
        self.tracks.append(track)

    def add_at(self, track, pos):
        self.tracks.insert(track, pos)

    def remove(self, pos):
        del(self.tracks[pos])

    def save(self, filename=''):
        if not filename:
            filename = self.name
        pickle.dump(self.tracks, filename)

    def load(self, filename=''):
        if not filename:
            filename = self.name
        self.tracks = pickle.load(filename)

    def save_tracks(self, path):
        for track in self.tracks:
            track.save(path)


class Track:
    def __init__(self, data, service=None):
        self._data = data
        if service == 'soundcloud' or isinstance(self._data, soundcloud.resource.Resource):
            self.title = self._data.title
            # self.stream_url = self._data.stream_url
            self.duration = self._data.duration // 1000  # ms
            self._service = 'soundcloud'
            self.id = self._data.id
            self.original_format = self._data.original_format
        elif service == 'pleer':
            if self._data['artist'] == '' or self._data['track'] == '':
                self.title = '%s%s' % (self._data['artist'], self._data['track'])
            else:
                self.title = '%s - %s' % (self._data['artist'], self._data['track'])
            # self.stream_url = self._data.stream_url
            self.duration = int(self._data['lenght'])
            self._service = 'pleer'
            self.id = self._data['id']
            self.original_format = 'mp3'
        else:
            raise "Invalid service name"

    def stream_url(self):
        url = None
        if self._service == 'soundcloud':
            url = sc_get_stream_url(track=self)
        elif self._service == 'pleer':
            url = pl_get_stream_url(track=self)
        return url

    def save(self, path=''):
        result = None
        if self._service == 'soundcloud':
            result = sc_save_track(track=self)
        elif self._service == 'pleer':
            result = pl_save_track(track=self)
        return result

    def search_related(self):
        result = None
        if self._service == 'soundcloud':
            result = sc_search_related(track=self)
        elif self._service == 'pleer':
            result = pl_search_related(track=self)
        return result


def sc_get_track(track_id):
    return Track(_client.get('/tracks/%i' % track_id), service='soundcloud')

def sc_get_stream_url(track_id=-1, track=None):
    if not track:
        assert id > 0
        track = sc_get_track(track_id)
    return "%s?client_id=%s" % (track._data.stream_url, soundcloud_client_id)

def sc_search_tracks(text):
    return [Track(x, service='soundcloud') for x in _client.get('/tracks', q=text)]

def sc_search_related(track_id=-1, track=None):
    if not track:
        assert id > 0
        track = sc_get_track(track_id)
    return [Track(x, service='soundcloud') for x in _client.get('/tracks/%i/related' % track.id)]

def sc_save_track(track_id=-1, track=None, path=''):
    if len(path) and path[len(path)-1] != os.sep:
        path += os.sep
    if not track:
        assert track_id > 0
        track = sc_get_track(track_id)
    url = track.stream_url()
    r = requests.get(url)
    if r.status_code == 200:
        filename = path + track.title + '.' + track.original_format
        f = open(filename, 'wb')
        for data in r.iter_content():
            f.write(data)
        f.close()
        print('Saved to "%s"' % filename)
        return True

def sc_load_playlist(name):
    playlists = _client.get('/me/playlists')
    index = -1
    for i in range(len(playlists)):
        if playlists[i].title == name:
            index = i
            break
    if index != -1:
        tracks = []
        for track in playlists[index].tracks:
            t = Track(soundcloud.resource.Resource(track), service='soundcloud')
            tracks.append(t)
        return tracks

def sc_save_playlist(name, playlist):
    query = []
    for track in playlist.tracks:
        if track._service == 'soundcloud':
            query.append(dict(id=track.id))
    playlists = _client.get('/me/playlists')
    # remove all older playlists
    for p in playlists:
        if p.title == name:
            _client.delete('/playlists/%i' % p.id)
    # save new
    _client.post('/playlists', playlist={'title': name, 'sharing': 'public', 'tracks': query})

def pl_get_track(track_id):
    return Track(_pleer.tracks_get_info(track_id), service='pleer')

def pl_get_stream_url(track_id=-1, track=None):
    if track:
        track_id = track.id
    response = _pleer.tracks_get_download_link(track_id)
    if response['success']:
        return response['url']

def pl_search_tracks(text):
    response = _pleer.tracks_search(params={'query': text})
    tracks = []
    if not response['success']:
        return tracks
    for track_id in response['tracks'].keys():
        track = Track(response['tracks'][track_id], service='pleer')
        tracks.append(track)
    return tracks

def pl_save_track(track_id=-1, track=None, path=''):
    if len(path) and path[len(path)-1] != os.sep:
        path += os.sep
    if not track:
        assert track_id > 0
        track = pl_get_track(track_id)
    response = _pleer.tracks_get_download_link(track_id, reason='save')
    if response['success']:
        url = response['url']
        r = requests.get(url)
        if r.status_code == 200:
            filename = path + track.title + '.' + track.original_format
            f = open(filename, 'wb')
            for data in r.iter_content():
                f.write(data)
            f.close()
            return True

def pl_search_related(track_id=-1, track=None):
    return []

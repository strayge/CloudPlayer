# -*- coding:utf-8 -*-

"""
@author: amureki
@contact: http://twitter.com/amureki
@license MIT License, see LICENSE file

Copyright (C) 2015
"""

import requests
from time import time

API_CORE_URL = u'http://api.pleer.com'
API_TOKEN_URL = u'%s/token.php' % API_CORE_URL
API_URL = u'%s/index.php' % API_CORE_URL


class PleerApi(object):
    def __init__(self, app_id=None, app_key=None):
        self.app_id = app_id
        self.app_key = app_key

        self.token_expire_time = None

        if not app_id or not app_key:
            raise AuthorizationError(u'Необходимо ввести идентификатор и ключ')
        self.token = self.get_access_token()

    def _check_token(self):
        if time() >= self.token_expire_time - 10:
            self.token = self.get_access_token()

    def get_access_token(self):
        auth = (self.app_id, self.app_key)
        data = {u'grant_type': u'client_credentials'}
        response = requests.post(API_TOKEN_URL, auth=auth, data=data)
        response_json = response.json()
        self.token_expire_time = time() + response_json.get(u'expires_in')
        return response_json.get(u'access_token')

    def tracks_search(self, params):
        self._check_token()
        data = {
            u'access_token': self.token,
            u'method': u'tracks_search'
        }
        data.update(params)
        response = requests.post(url=API_URL, data=data)
        return response.json()

    def tracks_get_info(self, track_id):
        self._check_token()
        data = {
            u'access_token': self.token,
            u'method': u'tracks_get_info',
            u'track_id': track_id
        }
        response = requests.post(url=API_URL, data=data)
        return response.json()

    def tracks_get_lyrics(self, track_id):
        self._check_token()
        data = {
            u'access_token': self.token,
            u'method': u'tracks_get_lyrics',
            u'track_id': track_id
        }
        response = requests.post(url=API_URL, data=data)
        return response.json()

    def tracks_get_download_link(self, track_id, reason=u'listen'):
        self._check_token()
        data = {
            u'access_token': self.token,
            u'method': u'tracks_get_download_link',
            u'track_id': track_id,
            u'reason': reason
        }
        response = requests.post(url=API_URL, data=data)
        return response.json()

    def get_top_list(self, list_type=1, page=1, language=u'en'):
        self._check_token()
        data = {
            u'access_token': self.token,
            u'method': u'get_top_list',
            u'list_type': list_type,
            u'page': page,
            u'language': language,
        }
        response = requests.post(url=API_URL, data=data)
        return response.json()

    def get_suggest(self, part):
        self._check_token()
        data = {
            u'access_token': self.token,
            u'method': u'get_suggest',
            u'part': part,
        }
        response = requests.post(url=API_URL, data=data)
        return response.json()


class AuthorizationError(Exception):
    pass
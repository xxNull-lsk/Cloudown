import json
import base64
from urllib.request import urlopen
from urllib.error import *
import logging


class Aria2:
    timeout = 1

    def __init__(self, server_url, token=None, timeout=1):
        self.server_url = server_url
        self.id = 'test'
        self.timeout = timeout
        if token is not None:
            self.token = 'token:{}'.format(token)
        else:
            self.token = None

    def add_uri(self, uri, params=None):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.addUri',
            'params': [
                [uri],
                {
                    'referer': uri
                }
            ]
        }

        if params is not None:
            for k in params:
                req['params'][1][k] = params[k]

        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        c = urlopen(self.server_url, req, timeout=self.timeout)
        return json.loads(c.read())

    @staticmethod
    def file_to_base64(file_name):
        with open(file_name, 'rb') as f:
            base64_data = base64.b64encode(f.read())
        trans_base64 = str(base64_data).lstrip('b').strip('\'')
        return trans_base64

    def add_torrent(self, torrent_file):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.addTorrent',
            'params': [
                self.file_to_base64(torrent_file)
            ]
        }
        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        c = urlopen(self.server_url, req, timeout=self.timeout)
        return json.loads(c.read())

    def add_metalink(self, metalink, dest_path):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.addMetalink',
            'params': [
                [metalink],
                {
                    'refer': metalink,
                    'dir': dest_path
                }
            ]
        }
        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        c = urlopen(self.server_url, req, timeout=self.timeout)
        return json.loads(c.read())

    def remove(self, task_id):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.remove',
            'params': [
                task_id
            ]
        }
        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        c = urlopen(self.server_url, req, timeout=self.timeout)
        return json.loads(c.read())

    def remove_stoped(self, task_id):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.removeDownloadResult',
            'params': [
                task_id
            ]
        }
        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        try:
            c = urlopen(self.server_url, req, timeout=self.timeout)
            return json.loads(c.read())
        except Exception as err:
            logging.error("remove_stoped failed!" + str(err))
            return None

    def pause(self, task_id, force=False):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.pause',
            'params': [
                task_id
            ]
        }
        if force:
            req['method'] = 'aria2.forcePause'
        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        try:
            c = urlopen(self.server_url, req, timeout=self.timeout)
            return json.loads(c.read())
        except Exception as err:
            logging.error(str(err))

    def unpause(self, task_id):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.unpause',
            'params': [
                task_id
            ]
        }
        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        try:
            c = urlopen(self.server_url, req, timeout=self.timeout)
            return json.loads(c.read())
        except Exception as err:
            logging.error(str(err))
            return {}

    def get_status(self, task_id):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.tellStatus',
            'params': [
                task_id
            ]
        }
        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        c = urlopen(self.server_url, req, timeout=self.timeout)
        return json.loads(c.read())

    def get_uri(self, task_id):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.getUris',
            'params': [
                task_id
            ]
        }
        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        c = urlopen(self.server_url, req, timeout=self.timeout)
        return json.loads(c.read())

    def get_files(self, task_id):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.getFiles',
            'params': [
                task_id
            ]
        }
        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        c = urlopen(self.server_url, req, timeout=self.timeout)
        return json.loads(c.read())

    def get_peers(self, task_id):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.getPeers',
            'params': [
                task_id
            ]
        }
        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        c = urlopen(self.server_url, req, timeout=self.timeout)
        return json.loads(c.read())

    def get_servers(self, task_id):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.getServers',
            'params': [
                task_id
            ]
        }
        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        c = urlopen(self.server_url, req, timeout=self.timeout)
        return json.loads(c.read())

    def get_active_tasks(self):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.tellActive',
            'params': []
        }
        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        c = urlopen(self.server_url, req, timeout=self.timeout)
        return json.loads(c.read())

    def get_waiting_tasks(self):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.tellWaiting',
            'params': [0, 999]
        }
        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        c = urlopen(self.server_url, req, timeout=self.timeout)
        return json.loads(c.read())

    def get_stopped_tasks(self):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.tellStopped',
            'params': [0, 999]
        }
        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        try:
            c = urlopen(self.server_url, req, timeout=self.timeout)
            return json.loads(c.read())
        except HTTPError as err:
            print(err)

    def get_task_option(self, task_id):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.getOption',
            'params': [
                task_id
            ]
        }
        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        c = urlopen(self.server_url, req)
        return json.loads(c.read())

    def set_task_option(self, task_id, options):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.changeOption',
            'params': [task_id, options]
        }
        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        c = urlopen(self.server_url, req, timeout=self.timeout)
        return json.loads(c.read())

    def get_system_option(self):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.getGlobalOption',
            'params': []
        }
        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        try:
            c = urlopen(self.server_url, req, timeout=self.timeout)
            return json.loads(c.read())
        except Exception as err:
            logging.error('{0}: {1}'.format(self.server_url, str(err)))
            return None

    def set_system_option(self, options):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.changeGlobalOption',
            'params': [options]
        }
        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        c = urlopen(self.server_url, req, timeout=self.timeout)
        return json.loads(c.read())

    def get_system_status(self):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.getGlobalStat',
            'params': []
        }
        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        c = urlopen(self.server_url, req, timeout=self.timeout)
        return json.loads(c.read())

    def get_version(self):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.getVersion',
            'params': []
        }
        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        c = urlopen(self.server_url, req, timeout=self.timeout)
        return json.loads(c.read())

    def get_session(self):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.getSessionInfo',
            'params': []
        }
        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        c = urlopen(self.server_url, req, timeout=self.timeout)
        return json.loads(c.read())

    def shutdown(self):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.shutdown',
            'params': []
        }
        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        c = urlopen(self.server_url, req, timeout=self.timeout)
        return json.loads(c.read())

    def save_session(self):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'aria2.saveSession',
            'params': []
        }
        if self.token is not None:
            req['params'].insert(0, self.token)
        req = bytes(json.dumps(req), 'utf-8')
        c = urlopen(self.server_url, req, timeout=self.timeout)
        return json.loads(c.read())

    def list_methods(self):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'system.listMethods'
        }
        req = bytes(json.dumps(req), 'utf-8')
        c = urlopen(self.server_url, req, timeout=self.timeout)
        return json.loads(c.read())

    def list_notifications(self):
        req = {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': 'system.listNotifications'
        }
        req = bytes(json.dumps(req), 'utf-8')
        c = urlopen(self.server_url, req, timeout=self.timeout)
        return json.loads(c.read())

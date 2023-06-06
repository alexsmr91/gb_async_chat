import logging
from threading import Thread
from time import time, sleep
from socket import *

from PyQt5.QtCore import QObject, pyqtSignal, QThread

from utils import *


from database.database import DBManager
from resp import *
from validators import Port, ClientCheck

PACKET_SIZE = 10000
DEFAULT_CHARSET = 'utf8'
TIMEOUT = 0.2

USER_STATUS = 'Online'
messages = []

logger = logging.getLogger('chat')


class ChatWatch(QObject):

    gotData = pyqtSignal()
    def __init__(self, parent, host, port, db_path):
        super().__init__()
        self.parent = parent
        self.chat = ChatClient(host, port, db_path)
        self.mess_len = 0

    def start(self):
        self.chat.t.start()

    def watcher(self):
        t3 = Thread(target=self.watch)
        t3.daemon = True
        t3.start()

    def watch(self):
        while True:
            if self.mess_len < len(self.chat.messages):
                self.gotData.emit()
                self.mess_len = len(self.chat.messages)
            QThread.msleep(200)



class ChatClient(metaclass=ClientCheck):
    port = Port()

    def __init__(self, host, port, db_path):
        super().__init__()
        self.host = host
        self.port = port
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.settimeout(TIMEOUT)
        self.db = DBManager(db_path)
        self.messages = []
        self.connect()
        self.t = Thread(target=self.recive)
        self.t.daemon = True
        self.block = False

    def __del__(self):
        self.s.close()

    def send_presence(self, login):
        obj = {
            'action': 'presence',
            'time': int(time()),
            'user': {
                'login': login,
                'status': USER_STATUS
            },
        }
        msg = json.dumps(obj)
        logger.info('Sending presence message')
        return self._send_msg(msg)

    def _send_msg(self, msg):
        self.block = True
        sleep(TIMEOUT)
        try:
            self.s.send(msg.encode(DEFAULT_CHARSET))
            data = self.s.recv(PACKET_SIZE)
            self.block = False
            return load_json_or_none(data.decode(DEFAULT_CHARSET))
        except Exception as e:
            logger.critical(e)
        self.block = False
        return {'error': INTERNAL_ERROR_500}

    def send_login(self, login):
        obj = {
            "action": "login",
            "time": int(time()),
            "login": login
        }
        msg = json.dumps(obj)
        logger.info('Sending login message')
        return self._send_msg(msg)

    def send_get_contacts(self, login):
        obj = {
            "action": "get_contacts",
            "time": int(time()),
            "login": login
        }
        msg = json.dumps(obj)
        logger.info('Sending get contacts message')
        return self._send_msg(msg)

    def send_add_contact(self, login, contact_login):
        obj = {
            "action": "add_contact",
            "contact_login": contact_login,
            "time": int(time()),
            "login": login
        }
        msg = json.dumps(obj)
        logger.info('Sending add contact message')
        return self._send_msg(msg)

    def send_remove_contact(self, login, contact_login):
        obj = {
            "action": "del_contact",
            "contact_login": contact_login,
            "time": int(time()),
            "login": login
        }
        msg = json.dumps(obj)
        logger.info('Sending remove contact message')
        return self._send_msg(msg)

    def send_message(self, from_client_login, to_client_login, message):
        obj = {
            "action": "send_message",
            "contact_login": to_client_login,
            "time": int(time()),
            "login": from_client_login,
            "message": message
        }
        msg = json.dumps(obj)
        logger.info('Sending message')
        return self._send_msg(msg)

    def connect(self):
        try:
            self.s.connect((self.host, self.port))
        except Exception:
            return 0
        else:
            logger.info('Connected')

    def recive(self):
        while True:
            if not self.block:
                try:
                    data = self.s.recv(PACKET_SIZE)
                    obj = load_json_or_none(data.decode(DEFAULT_CHARSET))
                    self.messages.append(obj)
                    print("---------------")
                    print(obj)
                except OSError as e:
                    pass

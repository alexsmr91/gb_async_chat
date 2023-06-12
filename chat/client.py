import logging
from threading import Thread
from time import time, sleep
from socket import *
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from cryptography.hazmat.primitives import serialization
from utils import *
from database.database import DBManager
from resp import *
from validators import Port, ClientCheck

logger = logging.getLogger('chat')


class ChatWatch(QObject):

    gotData = pyqtSignal()

    def __init__(self, parent: QObject, host: str, port: int, db_path: str):
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

    def __init__(self, host: str, port: int, db_path: str):
        super().__init__()
        self.host = host
        self.port = port
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.settimeout(TIMEOUT)
        self.db = DBManager(db_path)
        self.messages = []
        self.t = Thread(target=self.receive)
        self.t.daemon = True
        self.block = False
        self.private_key = ""
        self.public_key = ""

    def __del__(self):
        self.s.close()

    def send_presence(self, login: str) -> ObjDict:
        obj = ObjDict({
            'action': 'presence',
            'time': int(time()),
            'user': {
                'login': login,
                'status': USER_STATUS
            },
        })
        logger.info('Sending presence message')
        return self._send_msg(obj)

    def _send_msg(self, obj: ObjDict) -> ObjDict:
        msg_bytes = json.dumps(obj).encode(DEFAULT_CHARSET)
        if isinstance(self.public_key, RSAPublicKey):
            msg_bytes = encrypt_message(msg_bytes, self.public_key)
        return self.__send_msg(msg_bytes)

    def __send_msg(self, msg: bytes) -> ObjDict:
        self.block = True
        sleep(TIMEOUT)
        try:
            self.s.send(msg)
            data = self.s.recv(PACKET_SIZE)
        except Exception as e:
            logger.critical(e)
        else:
            self.block = False
            obj, resp = self.recived_data_handler(data)
            return obj
        self.block = False
        return ObjDict({'error': INTERNAL_ERROR_500})

    def refresh_keys(self) -> None:
        logger.info('Sending refresh keys message')
        self._send_msg(ObjDict({"action": "refresh_keys"}))
        self.private_key = generate_key_pair()
        pub = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)
        self.__send_msg(pub)

    def send_login(self, login: str, password_hash: str) -> ObjDict:
        obj = ObjDict({
            "action": "login",
            "time": int(time()),
            "login": login,
            "password_hash": password_hash
        })
        logger.info('Sending login message')
        return self._send_msg(obj)

    def send_get_contacts(self, login: str) -> ObjDict:
        obj = ObjDict({
            "action": "get_contacts",
            "time": int(time()),
            "login": login
        })
        logger.info('Sending get contacts message')
        return self._send_msg(obj)

    def send_add_contact(self, login: str, contact_login: str) -> ObjDict:
        obj = ObjDict({
            "action": "add_contact",
            "contact_login": contact_login,
            "time": int(time()),
            "login": login
        })
        logger.info('Sending add contact message')
        return self._send_msg(obj)

    def send_remove_contact(self, login: str, contact_login: str) -> ObjDict:
        obj = ObjDict({
            "action": "del_contact",
            "contact_login": contact_login,
            "time": int(time()),
            "login": login
        })
        logger.info('Sending remove contact message')
        return self._send_msg(obj)

    def send_message(self, from_client_login: str, to_client_login: str, message: str) -> ObjDict:
        obj = ObjDict({
            "action": "send_message",
            "contact_login": to_client_login,
            "time": int(time()),
            "login": from_client_login,
            "message": message
        })
        logger.info('Sending message')
        return self._send_msg(obj)

    def recived_data_handler(self, data: bytes) -> (ObjDict, ObjDict):
        resp = ObjDict({})
        obj = load_json_or_none(data, self.private_key)
        try:
            self.public_key = serialization.load_pem_public_key(data)
            resp = ObjDict({"action": KEY_CONFRIMINATION_203})
        except Exception as e:
            pass
        return obj, resp

    def receive(self):
        try:
            self.s.connect((self.host, self.port))
        except Exception as e:
            logger.error(e)
            logger.info('No connection')
        else:
            logger.info('Connected')
        while True:
            if not self.block:
                try:
                    resp = ObjDict({})
                    data = self.s.recv(PACKET_SIZE)
                    if data:
                        obj, resp = self.recived_data_handler(data)
                        self.messages.append(obj)
                    if resp:
                        self._send_msg(resp)
                except OSError as e:
                    pass

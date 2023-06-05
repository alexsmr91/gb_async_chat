import logging
from time import time
from socket import *
from utils import *


from chat.database.database import DBManager
from resp import *
from validators import Port, ClientCheck

PACKET_SIZE = 10000
DEFAULT_CHARSET = 'utf8'

USER_STATUS = 'Online'
messages = []

logger = logging.getLogger('chat')


class ChatClient(metaclass=ClientCheck):
    port = Port()

    def __init__(self, host, port, db_path):
        self.host = host
        self.port = port
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.settimeout(0.3)
        self.s.connect((self.host, self.port))
        self.db = DBManager(db_path)
        logger.info('Connected')

    def __del__(self):
        self.s.close()

    def send_presence(self, login):
        presence_obj = {
            'action': 'presence',
            'time': int(time()),
            'user': {
                'login': login,
                'status': USER_STATUS
            },
        }
        msg = json.dumps(presence_obj)
        logger.info('Sending presence message')
        return self.send_msg(msg)

    def send_msg(self, msg):
        try:
            self.s.send(msg.encode(DEFAULT_CHARSET))
            data = self.s.recv(PACKET_SIZE)
            return load_json_or_none(data.decode(DEFAULT_CHARSET))
        except Exception as e:
            logger.critical(e)
        return {'error': INTERNAL_ERROR_500}

    def send_login(self, login):
        presence_obj = {
            "action": "login",
            "time": int(time()),
            "login": login
        }
        msg = json.dumps(presence_obj)
        logger.info('Sending login message')
        return self.send_msg(msg)

    def send_get_contacts(self, login):
        presence_obj = {
            "action": "get_contacts",
            "time": int(time()),
            "login": login
        }
        msg = json.dumps(presence_obj)
        logger.info('Sending get contacts message')
        return self.send_msg(msg)

    def send_add_contact(self, login, contact_login):
        presence_obj = {
            "action": "add_contact",
            "contact_login": contact_login,
            "time": int(time()),
            "login": login
        }
        msg = json.dumps(presence_obj)
        logger.info('Sending add contact message')
        return self.send_msg(msg)

    def send_remove_contact(self, login, contact_login):
        presence_obj = {
            "action": "del_contact",
            "contact_login": contact_login,
            "time": int(time()),
            "login": login
        }
        msg = json.dumps(presence_obj)
        logger.info('Sending remove contact message')
        return self.send_msg(msg)

    def loop(self):
        while True:
            try:
                data = self.s.recv(PACKET_SIZE)
                msg = load_json_or_none(data.decode(DEFAULT_CHARSET))
                if 'user' in msg:
                    messages.append(f'{ttime()}\n{msg.user["account_name"]} : {msg.msg}')
            except OSError:
                pass

import argparse
import random
from time import time, sleep
from socket import *
import json
import logging
import log.client_log_config
from resp import *
DEFAULT_CHARSET = 'utf8'
USER_NAME = 'User'
USER_STATUS = 'Online'


class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.settimeout(0.2)
        self.s.connect((self.host, self.port))
        logger.info('Connected')

    def __del__(self):
        self.s.close()

    def send_presence(self, msg=''):
        presence_obj = {
            'action': 'presence',
            'time': int(time()),
            'type': 'status',
            'user': {
                'account_name': USER_NAME,
                'status': USER_STATUS
            },
            'msg': msg,
        }
        msg = json.dumps(presence_obj)
        logger.info('Sending presence message')
        return self.send_msg(msg)

    def send_msg(self, msg):
        try:
            self.s.send(msg.encode(DEFAULT_CHARSET))
            data = self.s.recv(10000)
            return data.decode(DEFAULT_CHARSET)
        except Exception as e:
            logger.critical(e)
        return INTERNAL_ERROR_500

    def loop(self):
        while True:
            print(f'{USER_NAME}: ')
            msg = input()
            self.send_presence(msg)


if __name__ == '__main__':
    logger = logging.getLogger('client')
    parser = argparse.ArgumentParser(description='Client side chat program')
    parser.add_argument(
        'addr',
        metavar='addr',
        type=str,
        help='Server address for connection'
    )
    parser.add_argument(
        '--port',
        metavar='p',
        type=int,
        default=7777,
        help='Port number for connection, default 7777'
    )
    args = parser.parse_args()
    PORT = args.port
    HOST = args.addr

    chat = ChatClient(HOST, PORT)
    USER_NAME = USER_NAME + ' - ' + str(random.randint(1, 1000))
    chat.loop()

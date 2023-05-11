import argparse
from collections import defaultdict
from socket import *

import select

from resp import *
import json
from json.decoder import JSONDecodeError
import logging
import log.server_log_config
from functools import wraps
import traceback
DEFAULT_CHARSET = 'utf8'
logger = logging.getLogger('server')


def log_enabler(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        msg = f'Функция {func.__name__} была вызвана из {traceback.extract_stack(limit=2)[-2][2]} с аргументами (args: {args}, kwargs: {kwargs})'
        logger.info(msg)
        return func(*args, **kwargs)
    return decorated


class ChatServer:
    def __init__(self, addr, port, max_conn=5):
        self.addr = addr
        self.port = port
        self.max_conn = max_conn
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.bind((self.addr, self.port))
        self.s.listen(self.max_conn)
        self.s.settimeout(0.2)
        self.clients = []
        self.responses = defaultdict(list)
        #self.messages = []

    def __del__(self):
        self.s.close()

    def load_json_or_none(self, data):
        try:
            obj = json.loads(data)
        except JSONDecodeError:
            obj = None
        return obj

    def read_requests(self, r_clients):
        for sock in r_clients:
            try:
                data = sock.recv(10000)
            except:
                logger.info('Client {} {} disconected'.format(sock.fileno(), sock.getpeername()))
                self.clients.remove(sock)
            else:
                obj = self.load_json_or_none(data.decode(DEFAULT_CHARSET))
                if obj:
                    msg = OK_200
                    log_msg = f'{sock.getpeername()} : {obj}'
                    #obj.setdefault('sock', sock)
                    #self.messages.append(obj)
                    self.responses[sock].append(obj)
                    for client in self.clients:
                        self.responses[client].append(obj)
                else:
                    msg = WRONG_JSON_OR_REQUEST_400
                    log_msg = f'{sock.getpeername()} WRONG JSON : "{data}"'
                logger.warning(log_msg)
                self.responses[sock].append(msg)

    def send_message(self, message, sock):
        msg = json.dumps(message)
        resp = msg.encode(DEFAULT_CHARSET)
        try:
            sock.send(resp)
        except:
            logger.info('Client {} {} disconected'.format(sock.fileno(), sock.getpeername()))
            sock.close()
            if sock in self.clients:
                self.clients.remove(sock)

    def write_responses(self, reqs, w_clients):
        for sock in w_clients:
            if sock in reqs:
                if reqs[sock] != []:
                    msg = reqs[sock].pop()
                    self.send_message(msg, sock)

    @log_enabler
    def loop(self):
        while True:
            try:
                client, addr = self.s.accept()
            except OSError as e:
                pass
            else:
                logger.info(f'Connected {addr}')
                self.clients.append(client)
            finally:
                wait = 10
                r = []
                w = []
                try:
                    r, w, e = select.select(self.clients, self.clients, [], wait)
                except:
                    pass
                self.read_requests(r)
                if self.responses:
                    self.write_responses(self.responses, w)


@log_enabler
def main():

    logger.info('Starting server')
    parser = argparse.ArgumentParser(description='Server side chat program')
    parser.add_argument(
        '--port',
        metavar='p',
        type=int,
        default=7777,
        help='Port number for listening, default 7777',
    )
    parser.add_argument(
        '--addr',
        metavar='ip',
        type=str,
        default='0.0.0.0',
        help='IP address for listening, default 0.0.0.0',

    )
    args = parser.parse_args()
    PORT = args.port
    ADDR = args.addr

    server = ChatServer(ADDR, PORT)
    server.loop()


if __name__ == '__main__':
    main()

import argparse
from socket import *
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

    def __del__(self):
        self.s.close()

    @log_enabler
    def load_json_or_none(self, data):
        try:
            obj = json.loads(data)
        except JSONDecodeError:
            obj = None
        return obj

    @log_enabler
    def loop(self):
        while True:
            client, addr = self.s.accept()
            logger.info("Connected")
            data = client.recv(1000000).decode(DEFAULT_CHARSET)
            obj = self.load_json_or_none(data)
            if obj:
                msg = OK_200
                log_msg = f'{addr} : {obj}'
            else:
                msg = WRONG_JSON_OR_REQUEST_400
                log_msg = f'{addr} WRONG JSON : "{data}"'
            logger.info(log_msg)
            client.send(msg.encode(DEFAULT_CHARSET))


@log_enabler
def main():

    logger.info("Starting server")
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


if __name__ == "__main__":
    main()

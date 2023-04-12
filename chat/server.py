import argparse
from socket import *
from resp import *
import json
from json.decoder import JSONDecodeError
DEFAULT_CHARSET = 'utf8'


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

    def load_json_or_none(self, data):
        try:
            obj = json.loads(data)
        except JSONDecodeError:
            obj = None
        return obj

    def loop(self):
        while True:
            client, addr = self.s.accept()
            data = client.recv(1000000).decode(DEFAULT_CHARSET)
            obj = self.load_json_or_none(data)
            if obj:
                msg = OK_200
                log_msg = f'{addr} : {obj}'
            else:
                msg = WRONG_JSON_OR_REQUEST_400
                log_msg = f'{addr} WRONG JSON : "{data}"'
            print(log_msg)
            client.send(msg.encode(DEFAULT_CHARSET))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Server side chat program')
    parser.add_argument(
        '--port',
        metavar='p',
        type=int,
        default=7777,
        help='Port number for listening, default 7777'
    )
    parser.add_argument(
        '--addr',
        metavar='ip',
        type=str,
        default='0.0.0.0',
        help='IP address for listening, default 0.0.0.0'
    )
    args = parser.parse_args()
    PORT = args.port
    ADDR = args.addr

    server = ChatServer(ADDR, PORT)
    server.loop()

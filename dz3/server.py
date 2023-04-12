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
        print("Closing connection")
        self.s.close()

    def loop(self):
        while True:
            client, addr = self.s.accept()
            data = client.recv(1000000).decode(DEFAULT_CHARSET)
            try:
                obj = json.loads(data)
                print(addr, " : ", obj)
                msg = OK_200.encode(DEFAULT_CHARSET)
            except JSONDecodeError:
                print(f'{addr} WRONG JSON : "{data}"')
                msg = WRONG_JSON_OR_REQUEST_400.encode(DEFAULT_CHARSET)
            client.send(msg)


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

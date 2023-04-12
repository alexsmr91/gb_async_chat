import argparse
from time import time
from socket import *
import json
from json.decoder import JSONDecodeError
DEFAULT_CHARSET = 'utf8'
USER_NAME = "C0deMaver1ck"
USER_STATUS = "Yep, I am here!"


class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.connect((self.host, self.port))

    def __del__(self):
        self.s.close()

    def send_presence(self):
        presence_obj = {
            "action": "presence",
            "time": int(time()),
            "type": "status",
            "user": {
                "account_name": USER_NAME,
                "status": USER_STATUS
            }
        }
        msg = json.dumps(presence_obj)
        return self.send_msg(msg)

    def send_msg(self, msg):
        self.s.send(msg.encode(DEFAULT_CHARSET))
        data = self.s.recv(1000000)
        return data.decode(DEFAULT_CHARSET)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Client side chat program')
    parser.add_argument(
        'addr',
        metavar='addr',
        type=str,
        help='Server addres for connection'
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
    print(chat.send_presence())

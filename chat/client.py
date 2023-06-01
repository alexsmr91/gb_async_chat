import argparse
import random
from json import JSONDecodeError
from threading import Thread
from time import time, sleep
from datetime import datetime
from socket import *
import json
import logging
import log.client_log_config
from resp import *
import curses
from validators import Port, ClientCheck

PACKET_SIZE = 10000
DEFAULT_CHARSET = 'utf8'
USER_NAME = 'User'
USER_STATUS = 'Online'
messages = []


def ttime():
    return str(datetime.now().time())[0:8]


class ChatClient(metaclass=ClientCheck):
    port = Port()
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.settimeout(0.2)
        self.s.connect((self.host, self.port))
        logger.info('Connected')

    def __del__(self):
        self.s.close()

    def load_json_or_none(self, data):
        try:
            obj = json.loads(data)
        except JSONDecodeError:
            obj = None
        return obj

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
            data = self.s.recv(PACKET_SIZE)
            return data.decode(DEFAULT_CHARSET)
        except Exception as e:
            logger.critical(e)
        return INTERNAL_ERROR_500

    def loop(self):
        while True:
            try:
                data = self.s.recv(PACKET_SIZE)
                msg = self.load_json_or_none(data.decode(DEFAULT_CHARSET))
                if 'user' in msg:
                    messages.append(f'{ttime()}\n{msg["user"]["account_name"]} : {msg["msg"]}')
            except OSError:
                pass


class Render:
    __slots__ = ['s', 'max_height', 'max_width', 'chat_height', 'chat_width', 'inf_top', 'inf_left', 'inf_height',
                 'chat_top', 'chat_left', 'msg_top', 'msg_left', 'scroll_offset', 'max_rows', 'message', 'resized',
                 'new_messages', 'chat_lines']

    def __init__(self):
        self.s = curses.initscr()
        self.s.keypad(True)
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.inf_top, self.inf_left = 0, 0
        self.inf_height = 2
        self.scroll_offset = 0
        self.max_rows = 1000
        self.chat_lines = 0
        self.resize()
        self.message = ''

    def resize(self):
        self.max_height, self.max_width = self.s.getmaxyx()
        self.chat_height, self.chat_width = self.max_height - 6, self.max_width - 1
        self.chat_top, self.chat_left = self.inf_top + self.inf_height + 1, self.inf_left
        self.msg_top, self.msg_left = self.chat_top + self.chat_height + 1, self.chat_left + 1
        self.resized = True
        self.new_messages = True

    def __del__(self):
        curses.nocbreak()
        self.s.keypad(False)
        curses.echo()
        curses.curs_set(1)
        curses.endwin()

    def run(self):
        t1 = Thread(target=self.draw)
        t2 = Thread(target=self.user_input)
        t1.daemon = True
        t2.daemon = False
        t1.start()
        t2.start()

    def draw(self):
        info_msg = '\n    PageUp и PageDown что бы листать историю чата, Enter  что бы отправить сообщение, Esc что бы выйти'
        text = ''
        while True:
            if self.resized:
                inf_pad = curses.newpad(3, self.chat_width)
                try:
                    inf_pad.addstr(info_msg)
                    inf_pad.refresh(0, 0, self.inf_top, self.inf_left, self.inf_top + self.inf_height,
                                    self.inf_left + self.chat_width)
                except curses.error:
                    pass
                chat_pad = curses.newpad(self.max_rows, self.chat_width)
                msg_pad = curses.newpad(2, self.chat_width - 1)
            while messages:
                self.new_messages = True
                text += f'{messages.pop()}\n'
            if self.new_messages:
                self.chat_lines = text.count('\n')
                self.scroll_offset = max(self.chat_lines - self.chat_height, 0)
                self.new_messages = False
            chat_pad.clear()
            msg_pad.clear()
            self.s.refresh()
            try:
                chat_pad.addstr(text)
                chat_pad.refresh(self.scroll_offset, 0, self.chat_top, self.chat_left,
                                 self.chat_top + self.chat_height - 1, self.chat_left + self.chat_width)
            except curses.error:
                pass
            try:
                msg_pad.addstr(0, 0, self.message)
                msg_pad.refresh(0, 0, self.msg_top, self.msg_left, self.msg_top, self.msg_left + self.chat_width - 1)
            except curses.error:
                pass
            sleep(0.1)

    def user_input(self):
        while True:
            key = self.s.getch()
            if key == curses.KEY_NPAGE and self.scroll_offset < self.chat_lines - self.chat_height:
                self.scroll_offset += 1
            elif key == curses.KEY_PPAGE and self.scroll_offset > 0:
                self.scroll_offset -= 1
            elif key == 27:  # ESC
                break
            elif key == curses.KEY_RESIZE:  # Resizing terminal window
                self.resize()
            elif key == 10 and self.message:  # Enter
                chat.send_presence(msg=self.message)
                messages.append(f'{ttime()}\n{USER_NAME} : {self.message}')
                self.message = ''
            elif key == 8:  # Backspace
                self.message = self.message[0:len(self.message)-1]
            elif 31 < key < 256 or 1039 < key < 1104 or key in (1025, 1105):
                self.message += chr(key)
            #else:
            #    self.message += f'${key}'


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
        'login',
        metavar='login',
        type=str,
        help='Your login'
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
    login = args.login

    chat = ChatClient(HOST, PORT)
    USER_NAME = login
    chat.send_presence(msg='вошел в чат')
    messages.append(f'{ttime()}\n{USER_NAME} : вошел в чат')
    renderer = Render()
    renderer.run()

    t3 = Thread(target=chat.loop)
    t3.daemon = True
    t3.start()

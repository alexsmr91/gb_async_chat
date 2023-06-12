import argparse
from collections import defaultdict
from time import time
from socket import *
import select
from typing import List, Dict, DefaultDict

from resp import *
import json
from json.decoder import JSONDecodeError
import logging
import log.server_log_config
from functools import wraps
import traceback
from validators import Port, ServerCheck
from database.database import DBManager
from config import *
from crypto import *
from cryptography.hazmat.primitives import serialization

logger = logging.getLogger('chat_server')


def log_enabler(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        msg = f'Функция {func.__name__} была вызвана из {traceback.extract_stack(limit=2)[-2][2]} с аргументами (args: {args}, kwargs: {kwargs})'
        logger.info(msg)
        return func(*args, **kwargs)
    return decorated


class ObjDict(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            return None

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            return None


class ChatServer(metaclass=ServerCheck):
    port = Port()
    clients: List[socket]
    secured: Dict[socket, bool]
    responses: DefaultDict[socket, List[bytes]]
    client_logins: dict
    private_keys: dict
    public_keys: dict

    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.bind((self.addr, self.port))
        self.s.listen(MAX_CONNECTIONS)
        self.s.settimeout(TIME_OUT)
        self.db = DBManager(DB_DEF_NAME)
        self.clients = []
        self.secured = {}
        self.responses = defaultdict(list)
        self.client_logins = {}
        self.private_keys = {}
        self.public_keys = {}

    def __del__(self):
        self.s.close()

    def obj2byte(self, obj: dict) -> bytes:
        return json.dumps(obj).encode(DEFAULT_CHARSET)

    def load_json_or_none(self, data: bytes, private_key="") -> ObjDict:
        if isinstance(private_key, RSAPrivateKey):
            try:
                data = decrypt_message(data, private_key)
            except Exception:
                pass
        data = data.decode(DEFAULT_CHARSET)
        try:
            obj = ObjDict(json.loads(data))
        except JSONDecodeError:
            obj = ObjDict({})
        return obj

    def message_handler(self, obj: ObjDict, sock: socket) -> ObjDict:
        if obj.action == KEY_CONFRIMINATION_203:
            self.secured[sock] = True
            return ObjDict({'status': OK_200})

        if obj.action == 'refresh_keys':
            self.refresh_keys(sock)
            return ObjDict({"": "no response"})

        if obj.action == 'login':
            login = obj.login
            password_hash = obj.password_hash
            ip = sock.getpeername()[0]
            client = self.db.add_new_login(login, password_hash, ip)
            if client:
                self.client_logins.setdefault(login, sock)
                return ObjDict({'status': OK_200, 'client': client})
            return ObjDict({'status': WRONG_LOGIN_PASSWORD_402})

        if obj.action == 'presence':
            login = obj.user['login']
            client = self.db.get_client_by_login(login)
            return ObjDict({'status': OK_200, 'client': client})

        if obj.action == 'get_contacts':
            login = obj.login
            contacts = self.db.get_contacts(login)
            return ObjDict({"response": CONFIRMATION_202, "alert": contacts})

        if obj.action == 'add_contact' or obj.action == 'del_contact':
            owner_login = obj.login
            client_login = obj.contact_login
            try:
                owner_id = self.db.get_client_by_login(owner_login).id
            except AttributeError:
                return ObjDict({"response": NOT_FOUND_404})
            try:
                client_id = self.db.get_client_by_login(client_login).id
            except AttributeError:
                return ObjDict({"response": NOT_FOUND_404})
            friends = self.db.are_friends(owner_id, client_id)

            if obj.action == 'add_contact':
                if not friends:
                    self.db.add_contact(owner_id, client_id)
                    return ObjDict({"response": CONFIRMATION_202})
                else:
                    # Уже есть в списке контактов
                    return ObjDict({"response": NOT_FOUND_404})
            else:
                if friends:
                    self.db.del_contact(owner_id, client_id)
                    return ObjDict({"response": CONFIRMATION_202})
                else:
                    # Некого удалять
                    return ObjDict({"response": NOT_FOUND_404})

        if obj.action == 'send_message':
            from_client_login = obj.login
            to_client_login = obj.contact_login
            res = self.send_message(from_client_login, to_client_login, obj.message)
            return res

    def send_message(self, from_client_login: str, to_client_login: str, message: str) -> ObjDict:
        try:
            to_sock = self.client_logins[to_client_login]
        except KeyError:
            client_id = self.db.get_client_by_login(to_client_login)
            if client_id:
                return ObjDict({'status': OFFLINE_410})
            else:
                return ObjDict({'status': NOT_FOUND_404})
        obj = ObjDict({
            "action": "send_message",
            "contact_login": to_client_login,
            "time": int(time()),
            "login": from_client_login,
            "message": message
        })
        logger.info('Add message to queue')
        self.responses[to_sock].append(self.obj2byte(obj))
        return ObjDict({'status': CONFIRMATION_202})

    def _send_message(self, msg: bytes, sock: socket) -> None:
        if self.secured[sock]:
            msg = encrypt_message(msg, self.public_keys[sock])
        self.__send_message(msg, sock)

    def __send_message(self, msg: bytes, sock: socket) -> None:
        try:
            sock.send(msg)
        except Exception as e:
            self.client_disconected(sock, e)
            sock.close()

    def client_disconected(self, sock: socket, e: Exception) -> None:
        logger.info(f'Client {sock.fileno()} : {sock.getpeername()} disconected. {e}')  # Error: {e}
        self.clients.remove(sock)
        self.private_keys.pop(sock)
        self.public_keys.pop(sock)
        self.secured.pop(sock)
        for key, value in self.client_logins.items():
            if value == sock:
                self.client_logins.pop(key)
                break

    def refresh_keys(self, sock: socket) -> None:
        self.secured[sock] = False
        self.public_keys[sock] = ""
        self.private_keys[sock] = generate_key_pair()
        public_key_bytes = self.private_keys[sock].public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.responses[sock].append(public_key_bytes)

    def read_requests(self, r_clients: List[socket]) -> None:
        for sock in r_clients:
            try:
                data = sock.recv(PACKET_SIZE)
            except Exception as e:
                self.client_disconected(sock, e)
            else:
                try:
                    client_public_key = serialization.load_pem_public_key(data)
                except Exception:
                    pass
                else:
                    self.public_keys[sock] = client_public_key
                    self.secured[sock] = True
                    self.responses[sock].append(self.obj2byte({'action': KEY_CONFRIMINATION_203}))
                    continue

                received_obj = self.load_json_or_none(data, self.private_keys[sock])
                obj = self.message_handler(received_obj, sock)
                if obj:
                    log_msg = f'{sock.getpeername()} : {received_obj}'
                else:
                    obj = {'status': WRONG_JSON_OR_REQUEST_400}
                    log_msg = f'{sock.getpeername()} WRONG JSON : "{data}"'
                logger.warning(log_msg)
                if obj != {"": "no response"}:
                    self.responses[sock].append(self.obj2byte(obj))

    def write_responses(self, reqs: DefaultDict[socket, List[bytes]], w_clients: List[socket]) -> None:
        for sock in w_clients:
            if sock in reqs:
                if reqs[sock]:
                    msg = reqs[sock].pop()
                    self._send_message(msg, sock)

    @log_enabler
    def loop(self) -> None:
        while True:
            try:
                client, addr = self.s.accept()
            except OSError as e:
                pass
            else:
                logger.info(f'Connected {addr}')
                self.clients.append(client)
                self.private_keys.setdefault(client, '')
                self.public_keys.setdefault(client, '')
                self.secured.setdefault(client, False)
            finally:
                wait = 10
                r = []
                w = []
                try:
                    r, w, e = select.select(self.clients, self.clients, [], wait)
                except Exception:
                    pass
                self.read_requests(r)
                if self.responses:
                    self.write_responses(self.responses, w)


@log_enabler
def main():

    logger.info('Starting chat_server')
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
    server = ChatServer(args.addr, args.port)
    server.loop()


if __name__ == '__main__':
    main()

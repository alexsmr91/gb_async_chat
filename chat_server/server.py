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
from validators import Port, ServerCheck
from database.database import DBManager

PACKET_SIZE = 10000
DEFAULT_CHARSET = 'utf8'
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

    def __init__(self, addr, port, max_conn=50):
        self.addr = addr
        self.port = port
        self.max_conn = max_conn
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.bind((self.addr, self.port))
        self.s.listen(self.max_conn)
        self.s.settimeout(0.2)
        self.clients = []
        self.responses = defaultdict(list)
        self.db = DBManager('server.sqlite.db')
        #self.messages = []

    def __del__(self):
        self.s.close()

    def load_json_or_none(self, data):
        try:
            obj = ObjDict(json.loads(data))
        except JSONDecodeError:
            obj = ObjDict({})
        return obj

    def message_handler(self, obj, ip):
        if obj.action == 'login':
            login = obj.login
            client = self.db.add_new_login(login, ip)
            return {'status': OK_200, 'client': client}

        if obj.action == 'presence':
            login = obj.user['login']
            client = self.db.get_client_by_login(login)
            return {'status': OK_200, 'client': client}

        if obj.action == 'get_contacts':
            login = obj.login
            contacts = self.db.get_contacts(login)
            return {"response": CONFIRMATION_202, "alert": contacts}

        if obj.action == 'add_contact' or obj.action == 'del_contact':
            owner_login = obj.login
            client_login = obj.contact_login
            try:
                owner_id = self.db.get_client_by_login(owner_login).id
            except AttributeError:
                return {"response": NOT_FOUND_404}
            try:
                client_id = self.db.get_client_by_login(client_login).id
            except AttributeError:
                return {"response": NOT_FOUND_404}
            friends = self.db.are_friends(owner_id, client_id)

            if obj.action == 'add_contact':
                if not friends:
                    self.db.add_contact(owner_id, client_id)
                    return {"response": CONFIRMATION_202}
                else:
                    # Уже есть в списке контактов
                    return {"response": NOT_FOUND_404}
            else:
                if friends:
                    self.db.del_contact(owner_id, client_id)
                    return {"response": CONFIRMATION_202}
                else:
                    # Некого удалять
                    return {"response": NOT_FOUND_404}


    def read_requests(self, r_clients):
        for sock in r_clients:
            try:
                data = sock.recv(PACKET_SIZE)
            except:
                logger.info('Client {} {} disconected'.format(sock.fileno(), sock.getpeername()))
                self.clients.remove(sock)
            else:
                obj = self.load_json_or_none(data.decode(DEFAULT_CHARSET))
                ip = r_clients[0].getpeername()[0]
                msg = self.message_handler(obj, ip)
                if msg:
                    log_msg = f'{sock.getpeername()} : {obj}'
                else:
                    msg = {'status': WRONG_JSON_OR_REQUEST_400}
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
    PORT = args.port
    ADDR = args.addr

    server = ChatServer(ADDR, PORT)
    server.loop()


if __name__ == '__main__':
    main()

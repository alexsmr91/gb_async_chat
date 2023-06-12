import json
from json import JSONDecodeError
from config import *
from crypto import *


class ObjDict(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            #raise AttributeError("No such attribute: " + name)
            return None

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            # raise AttributeError("No such attribute: " + name)
            return None


def load_json_or_none(data: bytes, private_key="") -> ObjDict:
    if isinstance(private_key, RSAPrivateKey):
        try:
            data = decrypt_message(data, private_key)
        except Exception:
            pass
    try:
        obj = ObjDict(json.loads(data.decode(DEFAULT_CHARSET)))
    except JSONDecodeError:
        obj = ObjDict({})
    return obj


def load_server_config(file_path: str) -> dict:
    setup_dict = {'host': '127.0.0.1', 'port': 7777}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                try:
                    key, value = line.strip().split('=')
                    setup_dict[key.strip()] = value.strip()
                except ValueError:
                    pass
    except FileNotFoundError:
        with open(file_path, 'w') as file:
            for key, value in setup_dict.items():
                file.write(f"{key}={value}\n")
    return setup_dict

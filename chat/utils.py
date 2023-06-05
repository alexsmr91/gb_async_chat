import json
from datetime import datetime
from json import JSONDecodeError


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


def load_json_or_none(data):
    try:
        obj = ObjDict(json.loads(data))
    except JSONDecodeError:
        obj = ObjDict({})
    return obj


def ttime():
    return str(datetime.now().time())[0:8]


def str2date(str):
    return datetime.strptime(str, "%Y-%m-%d").date()

import json
from config import *


def obj2byte(obj):
    return json.dumps(obj).encode(DEFAULT_CHARSET)

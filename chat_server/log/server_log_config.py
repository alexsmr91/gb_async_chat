import logging
from logging.handlers import TimedRotatingFileHandler

formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(module)s %(message)s')
handler = TimedRotatingFileHandler('chat_server.log', when="d", interval=1)
handler.setFormatter(formatter)
logger = logging.getLogger('chat_server')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

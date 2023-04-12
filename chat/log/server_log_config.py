import logging
from logging.handlers import TimedRotatingFileHandler

formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(module)s %(message)s')
handler = TimedRotatingFileHandler('server.log', when="d", interval=1)
handler.setFormatter(formatter)
logger = logging.getLogger('server')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

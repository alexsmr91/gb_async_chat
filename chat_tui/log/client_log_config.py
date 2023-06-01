import logging

formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(module)s %(message)s')
handler = logging.FileHandler('chat.log')
handler.setFormatter(formatter)
logger = logging.getLogger('chat')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

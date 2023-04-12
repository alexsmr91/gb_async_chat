import logging

formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(module)s %(message)s')
handler = logging.FileHandler('client.log')
handler.setFormatter(formatter)
logger = logging.getLogger('client')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

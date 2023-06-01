import dis
import logging
logger = logging.getLogger('server')


class Port:
    def __set__(self, instance, value):
        if value < 1024 or value > 65535:
            msg = f'Wrong port : {value}. Allowed from 1024 to 65535'
            logger.critical(msg)
            raise ValueError(msg)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


class ClientCheck(type):
    def __init__(self, clsname, bases, clsdict):
        methods_black_list = ['accept', 'listen']
        for func in clsdict:
            try:
                ret = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in ret:
                    # if i.opname == "LOAD_GLOBAL":
                    if i.argval in methods_black_list:
                        msg = f'Dont use method {i.argval}'
                        logger.critical(msg)
                        raise TypeError(msg)
        super().__init__(clsname, bases, clsdict)

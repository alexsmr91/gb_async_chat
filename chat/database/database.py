from os import path
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from chat.database.dbcore import Base

from chat.models.clients import Clients
from chat.models.contacts import Contacts
from chat.models.logins import Logins

DATABASE_NAME = 'database.db'


class Singleton(type):
    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = None

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
        return cls.__instance


class DBManager(metaclass=Singleton):
    def __init__(self, file_name=DATABASE_NAME):
        self.engine = create_engine(f'sqlite:///{file_name}', pool_recycle=3600)
        session = sessionmaker(bind=self.engine)
        self._session = session()
        if not path.isfile(file_name):
            Base.metadata.create_all(self.engine)

    def close(self):
        self._session.close()

    def add_client(self, login="", name="", surname="", birthday_date=datetime.now(), status=""):
        client = Clients(login=login, name=name, surname=surname, birthday_date=birthday_date, status=status)
        self._session.add(client)
        self._session.commit()
        return client

    def add_new_login(self, login, ip):
        client = self._session.query(Clients).filter_by(login=login).first()
        if not client:
            client = self.add_client(login=login)
        new_login = Logins(client_id=client.id, date_time=datetime.now(), ip_address=ip)
        self._session.add(new_login)
        self._session.commit()
        self.close()

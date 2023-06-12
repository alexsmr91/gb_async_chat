from os import path
from datetime import datetime
from typing import Optional, Type, List

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from database.dbcore import Base

from models.clients import Clients
from models.contacts import Contacts
from models.logins import Logins


class Singleton(type):
    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = None

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
        return cls.__instance


class DBManager(metaclass=Singleton):
    def __init__(self, file_name: str):
        self.engine = create_engine(f'sqlite:///{file_name}', pool_recycle=3600)
        session = sessionmaker(bind=self.engine)
        self._session = session()
        if not path.isfile(file_name):
            Base.metadata.create_all(self.engine)

    def close(self):
        self._session.close()

    def add_client(self, login: str = "", name: str = "", surname: str = "",
                   birthday_date: datetime.date = datetime.now().date(), status: str = "") -> Clients:
        client = Clients(login=login, name=name, surname=surname, birthday_date=birthday_date, status=status)
        self._session.add(client)
        self._session.commit()
        return client

    def add_contact(self, owner_id: int, client_id: int):
        contact = Contacts(owner_id=owner_id, client_id=client_id)
        self._session.add(contact)
        self._session.commit()
        self.close()

    def del_contact(self, owner_id: int, client_id: int):
        contact = self._session.query(Contacts).filter_by(owner_id=owner_id, client_id=client_id).one_or_none()
        self._session.delete(contact)
        self._session.commit()
        self.close()

    def get_client_by_login(self, login: str) -> Optional[Type[Clients]]:
        return self._session.query(Clients).filter_by(login=login).first()

    def get_client_by_id(self, client_id: int) -> Optional[Type[Clients]]:
        return self._session.query(Clients).filter_by(id=client_id).first()

    def get_contacts(self, login: str) -> List[str]:
        res = []
        try:
            client_id = self.get_client_by_login(login).id
        except AttributeError:
            pass
        else:
            for contact in self._session.query(Contacts).filter_by(owner_id=client_id):
                res.append(self.get_client_by_id(contact.client_id).login)
        return res

    def are_friends(self, owner_id: int, client_id: int) -> bool:
        res = self._session.query(Contacts).filter_by(owner_id=owner_id, client_id=client_id).one_or_none()
        return bool(res)

    def add_new_login(self, login: str, password_hash: str, ip: str) -> dict:
        client = self.get_client_by_login(login)
        if not client:
            client = self.add_client(login=login)
            client.set_password(password_hash)
        login_allowed = client.check_password(password_hash)
        new_login = Logins(client_id=client.id, date_time=datetime.now(), ip_address=ip, successful=login_allowed)
        self._session.add(new_login)
        self._session.commit()
        if login_allowed:
            client_dct = client.get_dict()
        else:
            client_dct = {}
        self.close()
        return client_dct

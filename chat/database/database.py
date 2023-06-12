import datetime
from os import path
from typing import Optional, Type, List

from sqlalchemy import create_engine, MetaData, Table, or_, and_
from sqlalchemy.orm import sessionmaker
from database.dbcore import Base

from models.contacts import Contacts
from models.messages import Message
from models.profile import Profile


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

    def renew_contacts(self, contacts: list) -> None:
        self.clear_table('contacts')
        for con in contacts:
            contact = Contacts(login=con)
            self._session.add(contact)
        self._session.commit()
        self.close()

    def clear_table(self, table: str) -> None:
        table = Table(table, MetaData())
        delete_statement = table.delete()
        self._session.execute(delete_statement)
        self._session.commit()

    def get_my_profile(self) -> Optional[Type[Profile]]:
        return self._session.query(Profile).filter_by().first()

    def renew_profile(self, login: str, name: str, surname: str, birthday_date: datetime.datetime, status: str) -> Profile:
        res = self.get_my_profile()
        if not res:
            res = Profile(login=login, name=name, surname=surname, birthday_date=birthday_date, status=status)
            self._session.add(res)
        else:
            res.login = login
            res.name = name
            res.surname = surname
            res.birthday_date = birthday_date
            res.status = status
        self._session.commit()
        return res

    def add_message(self, from_login: str, to_login: str, msg: str, time: datetime.time) -> str:
        message = Message(from_login=from_login, to_login=to_login, message=msg, date_time=time)
        self._session.add(message)
        self._session.commit()
        res = f'{message}'
        self.close()
        return res

    def get_chat_history(self, from_login: str, login: str) -> List[str]:
        res = []
        messages = self._session.query(Message).filter(
            or_(
                and_(Message.from_login == from_login, Message.to_login == login),
                and_(Message.from_login == login, Message.to_login == from_login)
            )
    ).order_by(Message.date_time.asc()).all()
        for message in messages:
            res.append(f'{message}')
        return res

    def clear_history(self, from_login: str, login: str):
        messages = self._session.query(Message).filter(
            or_(
                and_(Message.from_login == from_login, Message.to_login == login),
                and_(Message.from_login == login, Message.to_login == from_login)
            )
        ).delete()
        self._session.commit()
        self.close()

from os import path
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from chat.database.dbcore import Base

from chat.models.contacts import Contacts
from chat.models.history import History
from chat.models.profile import Profile

DATABASE_NAME = 'chat.db'


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

    def renew_contacts(self, contacts):
        self.clear_table('contacts')
        for con in contacts:
            contact = Contacts(login=con)
            self._session.add(contact)
        self._session.commit()
        self.close()


    def clear_table(self, table):
        table = Table(table, MetaData())
        delete_statement = table.delete()
        self._session.execute(delete_statement)
        self._session.commit()

    def renew_profile(self, login, name, surname, birthday_date, status):
        res = self.get_my_profile()
        if not res:
            profile = Profile(login=login, name=name, surname=surname, birthday_date=birthday_date, status=status)
            self._session.add(profile)
        else:
            res.login = login
            res.name = name
            res.surname = surname
            res.birthday_date = birthday_date
            res. status = status
        self._session.commit()
        self.close()

    def get_my_profile(self):
        return self._session.query(Profile).filter_by().first()

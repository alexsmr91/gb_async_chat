from sqlalchemy import Column, Integer, String, Date
from chat_server.database.dbcore import Base
from sqlalchemy.orm import relationship


class Clients(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    login = Column(String)
    name = Column(String)
    surname = Column(String)
    birthday_date = Column(Date)
    status = Column(String)

    def __repr__(self):
        return f'{self.login}({self.name} {self.surname})'
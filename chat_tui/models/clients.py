from sqlalchemy import Column, Integer, String, Date
from chat_tui.database.dbcore import Base
from sqlalchemy.orm import relationship


class Clients(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    login = Column(String)
    name = Column(String)
    surname = Column(String)
    birthday_date = Column(Date)
    status = Column(String)
    #contacts = relationship('Clients', secondary='contacts', back_populates='clients')
    #logins = relationship('Clients', secondary='logins', back_populates='clients')

    def __repr__(self):
        return f'{self.login}({self.name} {self.surname})'

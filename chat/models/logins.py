from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from chat.database.dbcore import Base
from chat.models.clients import Clients


class Logins(Base):
    __tablename__ = 'logins'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    date_time = Column(DateTime)
    ip_address = Column(String)
    client = relationship('Clients', backref='logins')


    def __repr__(self):
        return f'{self.client} {self.ip_address} {self.date_time}'

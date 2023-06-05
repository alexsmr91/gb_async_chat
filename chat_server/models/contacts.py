from sqlalchemy import Column, Integer, ForeignKey
from chat_server.database.dbcore import Base
from sqlalchemy.orm import relationship


class Contacts(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('clients.id'))
    client_id = Column(Integer, ForeignKey('clients.id'))
    owner = relationship('Clients', foreign_keys=[owner_id], backref='owned_contacts')
    client = relationship('Clients', foreign_keys=[client_id], backref='contacts')

    def __repr__(self):
        return f'{self.owner_id} - {self.client_id}'

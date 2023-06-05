from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from chat.database.dbcore import Base


class History(Base):
    __tablename__ = 'history'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('contacts.client_id'))
    date_time = Column(DateTime, server_default=func.now())
    message = Column(String)

    def __repr__(self):
        return f'{self.date_time}/n{self.message}'

from sqlalchemy import Column, Integer, String, DateTime, func
from database.dbcore import Base


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    from_login = Column(String)
    to_login = Column(String)
    date_time = Column(DateTime, server_default=func.now())
    message = Column(String)

    def __repr__(self):
        return f'{self.from_login} at {self.date_time}:\n{self.message}\n'

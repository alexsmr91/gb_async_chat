from sqlalchemy import Column, Integer, String
from database.dbcore import Base


class Contacts(Base):
    __tablename__ = 'contacts'

    client_id = Column(Integer, primary_key=True)
    login = Column(String)

    def __repr__(self):
        return f'{self.login}'

from sqlalchemy import Column, Integer, String, Date, func
from database.dbcore import Base


class Profile(Base):
    __tablename__ = 'profile'

    client_id = Column(Integer, primary_key=True)
    login = Column(String)
    name = Column(String)
    surname = Column(String)
    birthday_date = Column(Date, server_default=func.current_date())
    status = Column(String)

    def __repr__(self):
        return f'{self.login}'

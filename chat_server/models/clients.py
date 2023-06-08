from sqlalchemy import Column, Integer, String, Date, func
from database.dbcore import Base


class Clients(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    login = Column(String)
    name = Column(String)
    surname = Column(String)
    birthday_date = Column(Date, server_default=func.current_date())
    status = Column(String)

    def get_dict(self):
        res = {
            'client_id': self.id,
            'login': self.login,
            'name': self.name,
            'surname': self.surname,
            'birthday_date': str(self.birthday_date),
            'status': self.status
        }
        return res

    def __repr__(self):
        return f'{self.login}'

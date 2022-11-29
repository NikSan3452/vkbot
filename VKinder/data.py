import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config import settings

Base = declarative_base()
engine = sq.create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    """Класс описывающий пользователя

    Args:
        Base (Base): Базовый класс
    """
    __tablename__ = "user"
    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer)
    first_name = sq.Column(sq.String)
    last_name = sq.Column(sq.String)

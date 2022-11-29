from typing import Any
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


class FoundUser(Base):
    """Класс описывающий найденых пользователей, которые добавлены в понравившееся

    Args:
        Base (Base): Базовый класс
    """
    __tablename__ = "founduser"
    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer)
    first_name = sq.Column(sq.String)
    last_name = sq.Column(sq.String)
    top_photos = sq.Column(sq.String(1000))
    User_id = sq.Column(sq.Integer, sq.ForeignKey("user.id"))
    like = sq.Column(sq.Boolean)
    user = relationship(User)


def create_tables() -> None:
    """Создает таблицы
    """
    Base.metadata.create_all(engine)

def add_user(user: User) -> None: 
    """Добавляет новых пользователей

    Args:
        user (User): Пользователь
    """
    session.expire_on_commit = False
    session.add(user)
    session.commit()


def add_user_list(user: User) -> None:
    """Добавляет список пользователей

    Args:
        user (User): Список пользователей
    """
    session.expire_on_commit = False
    session.add_all(user)
    session.commit()


def get_viewed_user(user_id: Any, users_list: list[FoundUser]) -> FoundUser:
    list = session.query(FoundUser).filter(FoundUser.User_id == user_id).all()
    users = set()
    found_users = []
    for item in list:
        users.add(item.vk_id)
    for item in users_list:
        if item["id"] not in users:
            found_users.append(item)
    return found_users
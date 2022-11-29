from typing import Any, Optional
import requests
import vk_api
from data import User
import data
import json

from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange
from messages import *
from config import settings


vk = vk_api.VkApi(token=settings.VK_GROUP_TOKEN)
longpoll = VkLongPoll(vk)


def get_params(add_params: Optional[dict] = None) -> dict:
    """Получаем параметры

    Args:
        add_params (dict, optional): Параметры, по умолчанию None

    Returns:
        dict: Параметры
    """
    params = {"access_token": settings.VK_USER_TOKEN, "v": settings.V}
    if add_params:
        params.update(add_params)
    return params


def write_msg(user_id: int, message: str, attachment: Optional[str] = "") -> None:
    """Сообщения бота

    Args:
        user_id (int): ID пользователя
        message (str): Сообщение
        attachment (str, optional): Вложение, по умолчанию пустая строка - "".
    """
    vk.method(
        "messages.send",
        {
            "user_id": user_id,
            "message": message,
            "random_id": randrange(10**7),
            "attachment": attachment,
        },
    )

class VkBot:
    """Основной класс описывающий бота
    """

    def __init__(self, user_id: int) -> None:
        self.user: User = data.User
        self.id: int = self.user.id
        self.user_id: int = user_id
        self.commands: list[str] = ["ПРИВЕТ", "СТАРТ"]
        self.first_name: Optional[str] = ""
        self.last_name: Optional[str] = ""
        self.city: str = 0
        self.age_from: int = 0
        self.age_to: int = 0
        self.sex: int = 0
        self.users_list: list = []

    def get_user_name(self) -> tuple(str):
        """Получаем имя и фамилию пользователя

        Args:
            self (self): self

        Returns:
            _type_: Имя и фамилия
        """
        response = requests.get(
            "https://api.vk.com/method/users.get",
            get_params({"user_ids": self.user_id}),
        )
        resp = response.json()
        items = resp.get("response", {})
        if not items:
            return None
        for user_info in items:
            self.first_name = user_info["first_name"]
            self.last_name = user_info["last_name"]
        return self.first_name, self.last_name

    
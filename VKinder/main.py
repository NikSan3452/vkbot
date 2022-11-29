from typing import Any, Optional
import requests
import vk_api
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

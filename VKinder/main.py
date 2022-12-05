import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange
from messages import *
import requests
import vk_api
import data
import json

GROUP_TOKEN = ""
USER_TOKEN = ""

vk = vk_api.VkApi(token=GROUP_TOKEN)
longpoll = VkLongPoll(vk)


def get_params(add_params: dict = None):
    params = {"access_token": USER_TOKEN, "v": "5.131"}
    if add_params:
        params.update(add_params)
    return params


def write_msg(user_id, message, attachment=""):
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

    # Инициализация бота

    def __init__(self, user_id):
        self.user = data.User
        self.id = self.user.id
        self.user_id = user_id
        self.commands = ["ПРИВЕТ", "СТАРТ"]
        self.first_name = ""
        self.last_name = ""
        self.city = ""
        self.age_from = 0
        self.age_to = 0
        self.sex = 0
        self.relation = 0
        self.users_list = []

    # Получаем параметры пользователя
    def get_user_params_automatically(self):
        response = requests.get(
            "https://api.vk.com/method/users.get",
            get_params(
                {
                    "user_ids": self.user_id,
                    "fields": "bdate, age_from, age_to, sex, city, home_town, relation",
                }
            ),
        )

        # Для удобства переводим в формат json
        resp = response.json()
        items = resp.get("response", {})
        if not items:
            return None

        # Проходимся циклом по запросу
        for user_info in items:
            # Имя
            self.first_name = user_info.get("first_name", None)

            # Фамилия
            self.last_name = user_info.get("last_name", None)

            # Минимальный возраст. Находим как разницу между текущим временем и годом рождения
            min_age = user_info.get("bdate", None)
            if min_age is not None:
                self.age_from = datetime.date.today().year - int(min_age.split(".")[2])
            elif min_age == None:
                self.age_from = None

            # Максимальный. Находим как разницу между текущим временем и годом рождения
            max_age = user_info.get("bdate", None)
            if max_age is not None:
                self.age_to = datetime.date.today().year - int(max_age.split(".")[2])
            elif max_age == None:
                self.age_to = None

            # Пол. Меняем местами, чтобы не попасть под новый закон о пропаганде ЛГБТ
            sex = user_info.get("sex", None)
            if sex == 1:
                self.sex = 2
            elif sex == 2:
                self.sex = 1

            # Город
            if "home_town" in user_info:
                self.city = user_info["home_town"]
            elif "city" in user_info:
                self.city = user_info["city"]["title"]
            else:
                self.city = None

            # Семейное положение
            self.relation = user_info.get("relation", None)

        return (
            self.first_name,
            self.last_name,
            self.age_from,
            self.age_to,
            self.sex,
            self.city,
            self.relation,
        )

    # Отправка сообщений ботом
    def new_message(self, message):
        # Привет
        if message.upper() == self.commands[0]:
            return GREETING_MESSAGE

        # Старт
        elif message.upper() == self.commands[1]:
            return self.run()

        # Неизвестное сообщение
        else:
            return UNKNOWN_MESSAGE

    # Основной цикл
    def run(self):
        download = []

        self.get_user_params_automatically()

        exist = (
            data.session.query(data.User)
            .filter(data.User.vk_id == self.user_id)
            .first()
        )
        if not exist:
            self.user = data.User(
                vk_id=self.user_id, first_name=self.first_name, last_name=self.last_name
            )
            data.add_user(self.user)
        else:
            self.user = exist

        # Если параметров недостаточно, запросить ввод
        if self.city is None or self.city == "":
            self.get_city()
        elif self.age_from is None or self.age_from == 0:
            self.get_min_age()
        elif self.age_to is None or self.age_to == 0:
            self.get_max_age()
        elif self.sex is None or self.sex == 0:
            self.get_sex()
        elif self.relation is None or self.relation == 0:
            self.get_relation()

        # Поиск
        self.find_user()
        for users in self.users_list:
            Found_User = FoundUser(users, self.user.id)
            download.append(
                data.FoundUser(
                    vk_id=Found_User.vk_id,
                    first_name=Found_User.first_name,
                    last_name=Found_User.last_name,
                    top_photos=Found_User.top_photos,
                    User_id=Found_User.User_id,
                    like=Found_User.like,
                )
            )
            write_msg(self.user_id, CONTINUE_FIND_MESSAGE)
            for new_event in longpoll.listen():
                if new_event.type == VkEventType.MESSAGE_NEW and new_event.to_me:
                    if new_event.message.lower() == "да":
                        break
                    if new_event.message.lower() == "нет":
                        data.add_user_list(download)
                        self.get_json(
                            data.session.query(data.FoundUser)
                            .filter(data.FoundUser.User_id == self.user.id)
                            .all()
                        )
                        return self.new_message("привет")

    # город
    def get_city(self):
        write_msg(self.user_id, INPUT_TOWN_MESSAGE)
        for new_event in longpoll.listen():
            if new_event.type == VkEventType.MESSAGE_NEW and new_event.to_me:
                response = requests.get(
                    "https://api.vk.com/method/database.getCities",
                    get_params({"country_id": 1, "count": 1, "q": new_event.message}),
                )
                resp = response.json()
                items = resp.get("response", {}).get("items", [])
                if not items:
                    write_msg(self.user_id, UNKNOWN_TOWN_MESSAGE)
                    return self.get_city()
                else:
                    for city_title in items:
                        self.city = city_title["title"]
                        return self.city

    # минимальный возраст
    def get_min_age(self):
        write_msg(self.user_id, INPUT_MIN_AGE_MESSAGE)
        for new_event in longpoll.listen():
            if new_event.type == VkEventType.MESSAGE_NEW and new_event.to_me:
                self.age_from = int(new_event.message)
                return self.age_from

    # максимальный возраст
    def get_max_age(self):
        write_msg(self.user_id, INPUT_MAX_AGE_MESSAGE)
        for new_event in longpoll.listen():
            if new_event.type == VkEventType.MESSAGE_NEW and new_event.to_me:
                self.age_to = int(new_event.message)
                return self.age_to

    # Пол
    def get_sex(self):
        write_msg(self.user_id, INPUT_SEX_MESSAGE)
        for new_event in longpoll.listen():
            if new_event.type == VkEventType.MESSAGE_NEW and new_event.to_me:
                if (
                    new_event.message.lower() == "мужской"
                    or new_event.message.lower() == "м"
                ):
                    self.sex = 2
                    return self.sex
                elif (
                    new_event.message.lower() == "женский"
                    or new_event.message.lower() == "ж"
                ):
                    self.sex = 1
                    return self.sex
                else:
                    write_msg(self.user_id, UNKNOWN_MESSAGE)

    def get_relation(self):
        write_msg(self.user_id, INPUT_RELATION_MESSAGE)
        for new_event in longpoll.listen():
            if new_event.type == VkEventType.MESSAGE_NEW and new_event.to_me:
                if int(new_event.message) == 1:
                    self.relation = 1
                    return self.relation
                elif int(new_event.message) == 2:
                    self.relation = 2
                    return self.relation
                elif int(new_event.message) == 3:
                    self.relation = 3
                    return self.relation
                elif int(new_event.message) == 4:
                    self.relation = 4
                    return self.relation
                elif int(new_event.message) == 5:
                    self.relation = 5
                    return self.relation
                elif int(new_event.message) == 6:
                    self.relation = 6
                    return self.relation
                elif int(new_event.message) == 7:
                    self.relation = 7
                    return self.relation
                elif int(new_event.message) == 8:
                    self.relation = 8
                    return self.relation
                elif int(new_event.message) == 0:
                    self.relation = 0
                    return self.relation
                else:
                    write_msg(self.user_id, UNKNOWN_MESSAGE)

    # Поиск
    def find_user(self):
        users_list = []
        response = requests.get(
            "https://api.vk.com/method/users.search",
            get_params(
                {
                    "count": 1000,
                    "hometown": self.city,
                    "country": 1,
                    "sex": self.sex,
                    "age_from": self.age_from,
                    "age_to": self.age_to,
                    "fields": "is_closed",
                    "has_photo": 1,
                    "relation": self.relation,
                }
            ),
        )
        resp = response.json()
        items = resp.get("response", {}).get("items", [])
        if not items:
            return None
        for users_id in items:
            private = users_id["is_closed"]
            if private:
                pass
            else:
                users_list.append(users_id)
        self.users_list = data.get_viewed_user(self.user.id, users_list)
        return self.users_list

    def get_json(self, result):
        res = list()
        for i in result:
            photos = i.top_photos.split(",")
            photos_list = []
            for item in photos:
                photos_list.append(f"https://vk.com/{item}")
            d = {
                "id": f"https://vk.com/id{i.vk_id}",
                "first_name": i.first_name,
                "last_name": i.last_name,
                "photos": photos_list,
            }
            res.append(d)
            if len(res) > 9:
                break
        with open("result.json", "w", encoding="utf8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)


class FoundUser(VkBot):
    def __init__(self, user, user_id):
        self.vk_id = user["id"]
        self.first_name = user["first_name"]
        self.last_name = user["last_name"]
        self.top_photos = self.get_top_photos(self.vk_id)
        self.User_id = user_id
        self.like = self.giv_info()

    def get_top_photos(self, id):
        photos = []
        response = requests.get(
            "https://api.vk.com/method/photos.get",
            get_params(
                {"owner_id": id, "album_id": "profile", "extended": 1, "count": 1000}
            ),
        )
        resp = response.json()
        items = resp.get("response", {}).get("items", [])
        if not items:
            return None
        sorted_response = sorted(items, key=lambda x: x["likes"]["count"], reverse=True)
        for photo_id in sorted_response:
            photos.append(f"""photo{id}_{photo_id['id']}""")
        top_photos = ",".join(photos[:3])

        return top_photos

    def giv_info(self):
        write_msg(
            event.user_id,
            f"Имя: {self.first_name }\n"
            f"Фамилия: {self.last_name}\nСсылка: @id{self.vk_id}",
            self.top_photos,
        )

        write_msg(event.user_id, DO_YOU_LIKE_IT_MESSAGE)
        for new_event in longpoll.listen():
            if new_event.type == VkEventType.MESSAGE_NEW and new_event.to_me:
                if new_event.message.lower() == "да":
                    return 1

                if new_event.message.lower() == "нет":
                    return 0
                else:
                    write_msg(event.user_id, UNKNOWN_MESSAGE)


# запуск
if __name__ == "__main__":
    data.create_tables()
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            bot = VkBot(event.user_id)
            write_msg(event.user_id, bot.new_message(event.text))

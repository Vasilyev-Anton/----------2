import json
import random
from datetime import datetime
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

with open('config.json') as f:
    config = json.load(f)

vk = vk_api.VkApi(token=config['vk_api_token'])
vk_p = vk_api.VkApi(token=config['access_token'])
longpoll = VkLongPoll(vk)


class VkBot:
    def __init__(self, user_id):
        self.token = config['access_token']
        self.user_id = user_id
        self.commands = ['ПРИВЕТ', 'ПОИСК', 'ПОКА', 'УТОЧНИ ГОРОД', 'УТОЧНИ ВОЗРАСТ',
                         'УПС, ПО ТВОЕМУ ЗАПРОСУ НИЧЕГО НЕ НАШЛОСЬ, ДАВАЙ ЧТО-НИБУДЬ ИЗМЕНИМ И ПОПРОБУЕМ ЕЩЕ РАЗ?']
        self.photo_id_replace = str()
        self.user_data = dict()

    def get_user_profile(self):
        response = vk_p.method('users.get', {'user_ids': self.user_id, 'fields': 'bdate, city, sex'})
        for user_profile in response:
            user_name = user_profile['first_name']
            if event.message.upper() != self.commands[1]:
                user_data = {'user_name': user_name}
                return user_data
            if 'city' in user_profile:
                city_id = user_profile['city']['id']
            else:
                city_id = self.get_more_information('city_id')
            if 'bdate' in user_profile and len(user_profile['bdate']) >= 6:
                age = datetime.now().year - int(user_profile['bdate'][-4:])
            else:
                age = self.get_more_information('age')
            user_sex = user_profile['sex']
            self.user_data = {'user_name': user_name, 'user_city': city_id, 'user_sex': user_sex, 'age': age}
            return self.user_data

    def get_random_id(self):
        id_list = list()
        temp_list = list()
        response = vk_p.method('users.search',
                               {'city': self.user_data['user_city'], 'has_photo': 1,
                                'age_from': self.user_data['age'] - 3, 'age_to': self.user_data['age'] + 3, 'status': 6,
                                'sex': 1 if self.user_data['user_sex'] == 2 else 2, 'count': 1000})
        users_profile = response['items']
        if not users_profile:
            self.get_more_information('error')
        else:
            for list_users in users_profile:
                if list_users['is_closed'] is False:
                    temp_list.append(list_users)
            for item in temp_list:
                id_list.append(item['id'])
            random_id = random.choice(id_list)  # сюда постааить ссылку на метод из БД который будет проверять наличие пользователя в БД
            return random_id

    def get_photo_list(self):
        owner_id = self.get_random_id()
        unsorted_photo_dict = dict()
        response = vk_p.method('photos.get', {'owner_id': owner_id, 'album_id': 'profile', 'extended': 1})
        photo_response = response['items']
        for item in photo_response:
            likes_comments_count = (item['likes']['count'] + item['comments']['count'])
            photo_id = item['id']
            temp_dict = {str(photo_id): str(likes_comments_count)}
            unsorted_photo_dict.update(temp_dict)
        temp_list = sorted(unsorted_photo_dict.items(), reverse=True, key=lambda x: int(x[1]))
        sorted_list = [item[0] for item in temp_list[:3]]
        return owner_id, sorted_list

    def get_owner_id_and_photo(self):
        owner_id, sorted_list = self.get_photo_list()
        photo_id = list()
        for photo in sorted_list:
            photo_id.append(f',photo{owner_id}_{photo}')
        photo_id_str = str(photo_id)
        self.photo_id_replace = photo_id_str.replace("', '", ",")
        return owner_id, self.photo_id_replace

    def get_more_information(self, title):
        info = int
        if title == 'city_id':
            self.write_msg(self.user_id, self.new_message(self.commands[3]))
            info = self.get_city_id(str(self.event_tracking()))
        elif title == 'age':
            self.write_msg(self.user_id, self.new_message(self.commands[4]))
            info = int(self.event_tracking())
        elif title == 'error':
            info = self.write_msg(self.user_id, self.new_message(self.commands[5])), \
                   self.write_msg(self.user_id, self.new_message(event.text))
        return info

    @staticmethod
    def event_tracking():
        for events in longpoll.listen():
            if events.type == VkEventType.MESSAGE_NEW and events.to_me:
                text = events.text
                return text

    @staticmethod
    def get_city_id(city):
        response_city = vk_p.method('database.getCities', {'country_id': 1, 'q': city, 'count': 1})
        city_ = response_city['items']
        for city in city_:
            city_id = city['id']
            return city_id

    def new_message(self, message):
        if message.upper() == self.commands[0]:  # Привет
            return f'Привет, {self.get_user_profile()["user_name"]}! Я чат-бот, который найдет тебе пару'
        elif message.upper() == self.commands[1]:  # Поиск
            return f'{self.get_user_profile()["user_name"]}, смотри, что я нашёл!\n' \
                   f'https://vk.com/id{self.get_owner_id_and_photo()[0]}\n '
        elif message.upper() == self.commands[2]:  # Пока
            return f'Пока(('
        elif message.upper() == self.commands[3]:  # Уточни город
            return f'Уточни город:'
        elif message.upper() == self.commands[4]:  # Уточни возраст
            return f'Уточни возраст: '
        elif message.upper() == self.commands[5]:  # Упс, по твоему запросу ничего не нашлось...
            return f'Упс, по твоему запросу ничего не нашлось, давай что-нибудь изменим и попробуем еще раз?'
        else:
            return 'Не понимаю о чем ты...'

    def write_msg(self, user_id, message):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Привет', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('Поиск', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('Пока', color=VkKeyboardColor.SECONDARY)
        if event.text.upper() == self.commands[1]:
            vk.method('messages.send',
                      {'user_id': user_id, 'message': message, 'attachment': self.photo_id_replace,
                       'keyboard': keyboard.get_keyboard(), 'random_id': random.randrange(10 ** 7)})
        else:
            vk.method('messages.send',
                      {'user_id': user_id, 'message': message, 'keyboard': keyboard.get_keyboard(),
                       'random_id': random.randrange(10 ** 7)})


if __name__ == '__main__':
    print('Server started')
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            bot = VkBot(event.user_id)
            bot.write_msg(event.user_id, bot.new_message(event.text))
            print('Text: ', event.text)

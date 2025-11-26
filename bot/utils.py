from telebot import types
import requests
API_URL = 'http://127.0.0.1:8000/'


class AuthManager:
    def __init__(self):
        self.sessions = {}

    # =====================================================
    # =============== LOGIN + STORE TOKENS ================
    # =====================================================

    def login(self, chat_id, email, password):
        """
        Логинит пользователя и сохраняет access, refresh.
        """
        url = f"{API_URL}account/login/"

        data = {
            "email": email,
            "password": password
        }

        response = requests.post(url, json=data)

        if response.status_code != 200:
            return response

        tokens = response.json()

        self.sessions[chat_id] = {
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "user": {
                "id": tokens.get("id"),
                "role": tokens.get("role"),
                "first_name": tokens.get("first_name"),
                "last_name": tokens.get("last_name"),
            }
        }

        return response

    # =====================================================
    # =============== REFRESH ACCESS TOKEN =================
    # =====================================================

    def refresh_access(self, chat_id):
        """
        Пытается обновить access токен через refresh.
        """

        if chat_id not in self.sessions:
            return None

        refresh_token = self.sessions[chat_id]["refresh"]

        url = f"{API_URL}account/token/refresh/"
        response = requests.post(url, json={"refresh": refresh_token})

        # Refresh токен тоже умер → пользователь не авторизован
        if response.status_code != 200:
            return None

        data = response.json()

        # Обновляем access
        new_access = data.get("access")
        self.sessions[chat_id]["access"] = new_access

        # Если SimpleJWT настроен на ротацию refresh токенов
        if "refresh" in data:
            self.sessions[chat_id]["refresh"] = data.get("refresh")

        return new_access

    # =====================================================
    # =============== INTERNAL REQUEST WRAPPER =============
    # =====================================================

    def _request(self, chat_id, method, endpoint, data=None, params=None):
        """
        Делает запрос к API с токеном. Если токен истёк — обновляет.
        """       
        access = self.sessions[chat_id]["access"]

        headers = {"Authorization": f"Bearer {access}"}

        url = f"{API_URL}{endpoint}"

        # Первый запрос
        response = requests.request(method, url, json=data, params=params, headers=headers)

        # Если токен истёк — обновляем и повторяем
        if response.status_code == 401:
            new_access = self.refresh_access(chat_id)

            headers = {"Authorization": f"Bearer {new_access}"}
            response = requests.request(method, url, json=data, params=params, headers=headers)

        return response

    # =====================================================
    # ================= PUBLIC API METHODS =================
    # =====================================================

    def get(self, chat_id, endpoint, params=None):
        return self._request(chat_id, "GET", endpoint, params=params)

    def post(self, chat_id, endpoint, data=None):
        return self._request(chat_id, "POST", endpoint, data=data)

    def patch(self, chat_id, endpoint, data=None):
        return self._request(chat_id, "PATCH", endpoint, data=data)

    def delete(self, chat_id, endpoint, data=None):
        return self._request(chat_id, "DELETE", endpoint, data=data)

    # =====================================================
    # =================== USER HELPERS =====================
    # =====================================================

    def is_authenticated(self, chat_id):
        return chat_id in self.sessions

    def get_role(self, chat_id):
        if chat_id in self.sessions:
            return self.sessions[chat_id]["user"]["role"]
        return None

    def logout(self, chat_id):
        self.sessions.pop(chat_id, None)




def show_menu(bot, role, chat_id, message_id=None, edit=False):
    markup = types.InlineKeyboardMarkup()

    if role == 'student':
        markup.add(types.InlineKeyboardButton('Мои абонементы', callback_data='my_subscriptions'))
        markup.add(types.InlineKeyboardButton('Расписание занятий', callback_data='timetable'))
        markup.add(types.InlineKeyboardButton('Адрес и контакты', callback_data='adress_contacts'))
        markup.add(types.InlineKeyboardButton('Выйти', callback_data='exit'))
        
    elif role == 'parent':
        markup.add(types.InlineKeyboardButton('Мои абонементы', callback_data='my_subscriptions'))
        markup.add(types.InlineKeyboardButton('Мои дети', callback_data='my_childs_subscriptions'))
        markup.add(types.InlineKeyboardButton('Зарегистрировать ребенка', callback_data='register_child'))
        markup.add(types.InlineKeyboardButton('Расписание занятий', callback_data='timetable'))
        markup.add(types.InlineKeyboardButton('Адрес и контакты', callback_data='adress_contacts'))
        markup.add(types.InlineKeyboardButton('Выйти', callback_data='exit'))

    elif role == 'admin':
        markup.add(types.InlineKeyboardButton('Открыть панель администратора', callback_data='admin_panel'))
        markup.add(types.InlineKeyboardButton('Расписание занятий', callback_data='timetable'))
        markup.add(types.InlineKeyboardButton('Выйти', callback_data='exit'))

    if edit and message_id:
        bot.edit_message_text(
            "🏠 <b>Главное меню</b>",
            chat_id=chat_id,
            message_id=message_id,
            parse_mode='HTML',
            reply_markup=markup
        )
    else:
        bot.send_message(
            chat_id,
            "🏠 <b>Главное меню</b>",
            parse_mode='HTML',
            reply_markup=markup
        )




import requests
from telebot import types
from .utils import show_menu

API_URL="http://127.0.0.1:8000/account/"

class Auth:
    def __init__(self, bot, auth):
        self.bot = bot
        self.auth = auth
        self.user_data = {}
        self.rec_data = {}

        self.bot.callback_query_handler(func=lambda call:call.data=='login')(self.login)
        self.bot.callback_query_handler(func=lambda call:call.data=='register')(self.register)
        self.bot.callback_query_handler(func=lambda call:call.data.startswith('role_'))(self.get_role)
        self.bot.callback_query_handler(func=lambda call:call.data=='recovery_password')(self.start_recovery)


    def start_auth(self, message):
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton('Войти', callback_data='login'),
            types.InlineKeyboardButton('Регистрация', callback_data='register')
        )
        self.bot.send_message(message.chat.id, 'Добро пожаловать.', reply_markup=markup)

    def register(self, call):
        self.user_data[call.message.chat.id] = {}
        self.bot.send_message(call.message.chat.id, 'Введите логин: ')
        self.bot.register_next_step_handler(call.message, self.get_email)

    def get_email(self, message):
        email = message.text.strip()
        self.user_data[message.chat.id]['email'] = email

        self.bot.send_message(message.chat.id, 'Введите пароль: ')
        self.bot.register_next_step_handler(message, self.get_password)

    def get_password(self, message):
        password = message.text.strip()

        self.user_data[message.chat.id]['password'] = password

        self.bot.send_message(message.chat.id, 'Введите пароль повторно: ')
        self.bot.register_next_step_handler(message, self.get_p2)

    def get_p2(self, message):
        p2 = message.text.strip()
        if self.user_data[message.chat.id]['password'] != p2:
            self.bot.send_message(message.chat.id, 'Пароли не совпали. Введите пароль заново: ')
            self.user_data[message.chat.id].pop('password')
            self.bot.register_next_step_handler(message, self.get_password)
            return
        
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton('Родитель', callback_data=f'role_parent'),
            types.InlineKeyboardButton('Пользователь', callback_data=f'role_student')
        )
        self.bot.send_message(message.chat.id,'Укажите кто вы:', reply_markup=markup)

    def get_role(self, call):
        role = call.data.split('_')[1]
        self.user_data[call.message.chat.id]['role'] = role

        self.bot.send_message(call.message.chat.id, 'Введите ваше имя: ')
        self.bot.register_next_step_handler(call.message, self.get_name)


    def get_name(self, message):
        first_name = message.text.strip()
        self.user_data[message.chat.id]['first_name'] = first_name
            
        self.bot.send_message(message.chat.id, 'Введите фамилию: ')
        self.bot.register_next_step_handler(message, self.get_last_name)


    def get_last_name(self, message):
        last_name = message.text.strip()
        self.user_data[message.chat.id]['last_name'] = last_name
        
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(types.KeyboardButton(text='📞 Отправить номер', request_contact=True))
        self.bot.send_message(message.chat.id, 'Отправьте номер телефона(+996): ', reply_markup=markup)
        self.bot.register_next_step_handler(message, self.get_phone)
        
    
    def get_phone(self, message):
        chat_id = message.chat.id

        if message.contact:
            phone = message.contact.phone_number
        else:
            phone = message.text.strip()

        if phone.startswith('9'):
            phone = '+' + phone 
        if not phone or not phone.startswith("+") or not phone[1:].isdigit():
            self.bot.send_message(message.chat.id, f'Неверный формат номера ({phone}). Попробуйте ещё раз: ')
            self.bot.register_next_step_handler(message, self.get_phone)
            return

        self.user_data[message.chat.id]['phone'] = phone

        data = {
            'telegram_id':message.from_user.id,
            'email':self.user_data[message.chat.id]['email'],
            'password':self.user_data[message.chat.id]['password'],
            'role':self.user_data[message.chat.id]['role'],
            'first_name':self.user_data[message.chat.id]['first_name'],
            'last_name':self.user_data[message.chat.id]['last_name'],
            'phone':self.user_data[message.chat.id]['phone']
        }

        try:
            response = requests.post(f"{API_URL}register/",json=data)
            if response.status_code == 200:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('Войти', callback_data='login'))
                self.bot.send_message(message.chat.id, f'На вашу почту был отправлен код для активации. {self.user_data[message.chat.id]['email']}\nПосле активации нажмите войти.',
                                      reply_markup=markup)
            
            else:
                self.bot.send_message(message.chat.id, f'Ошибка при регистрации: {response.status_code}\n{response.text}')
        except Exception as e:
            self.bot.send_message(message.chat.id, f'Ошибка при регестрации: {e}')
        finally:
                self.user_data.pop(message.chat.id)

# ------------------LOGIN--------------------
    def login(self, call):
        self.user_data[call.message.chat.id] = {}
        self.bot.send_message(call.message.chat.id, 'Введите логин: ')
        self.bot.register_next_step_handler(call.message, self.get_email_login)

    def login_by_command(self, message):
        self.user_data[message.chat.id] = {}
        self.bot.send_message(message.chat.id, 'Введите логин: ')
        self.bot.register_next_step_handler(message, self.get_email_login)

    def get_email_login(self, message):
        email = message.text.strip()
        self.user_data[message.chat.id]['email'] = email

        self.bot.send_message(message.chat.id, 'Введите пароль: ')
        self.bot.register_next_step_handler(message, self.get_password_login)

    def get_password_login(self, message):
        chat_id = message.chat.id
        password = message.text.strip()
        self.user_data[message.chat.id]['password'] = password
        email = self.user_data[message.chat.id]['email']

        try:
            response = self.auth.login(chat_id, email, password)
            if response.status_code == 200:
                tokens = response.json()
                first_name = tokens.get('first_name')
                role = tokens.get('role')
                show_menu(self.bot, role, message.chat.id)
                self.bot.send_message(message.chat.id,f'Добро пожаловать, {first_name}! 🥳')  
                self.user_data.pop(chat_id)         
            elif response.status_code == 401:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('Забили пароль?', callback_data='recovery_password'))
                self.bot.send_message(
                    message.chat.id, 'Не найдено активной учетной записи с указанными данными. Попробуйте снова:',
                    reply_markup=markup)
                self.bot.register_next_step_handler(message, self.get_email_login)
            else:
                self.bot.send_message(message.chat.id, f'Ошибка при входе: {response.status_code}\n{response.text}')
        except Exception as e:
            self.bot.send_message(message.chat.id, f'Ошибка: {e}')

# -----------------------ResetPassword-------------------------------

    def start_recovery(self, call):
        self.user_data.pop(call.message.chat.id)
        self.rec_data[call.message.chat.id] = {}

        self.bot.send_message(call.message.chat.id, 'Введите email для восстановления(логин): ')
        self.bot.register_next_step_handler(call.message, self.get_email_for_recovery)

    def get_email_for_recovery(self, message):
        chat_id = message.chat.id
        email = message.text.strip()
        self.rec_data[message.chat.id]['email'] = email
        data = {'email':email}
        try:
            response = requests.post(f"{API_URL}password_reset/", json=data)
            if response.status_code==200:
                data = response.json()
                self.rec_data[chat_id]['uid'] = data['uid']
                self.rec_data[chat_id]['token'] = data['token']
                self.rec_data[chat_id]['code'] = data['code']
                self.bot.send_message(chat_id, 
                                      f'На вашу почту был отправлен код для активации. {email}\n'
                                      f'Введите код активации: '
                                      )
                self.bot.register_next_step_handler(message,self.get_code)
            else:
                self.bot.send_message(message.chat.id, f'Ошибка: {response.status_code}\n{response.text}')
        except Exception as e:
            self.bot.send_message(message.chat.id, f'Ошибка: {e}')

    def get_code(self, message):
        code = message.text.strip()
        if code != self.rec_data[message.chat.id]['code']:
            self.bot.send_message(message.chat.id, 'Неверный код для активации. Попробуйте снова: ')
            self.bot.register_next_step_handler(message,self.get_code)
            return
        self.bot.send_message(message.chat.id, 'Введите новый пароль: ')
        self.bot.register_next_step_handler(message,self.get_new_password)

    def get_new_password(self, message):
        password = message.text.strip()
        self.bot.send_message(message.chat.id,'Введите пароль повторно: ')
        self.bot.register_next_step_handler(message, self.get_new_p2, password)

    def get_new_p2(self,message, password):
        p2 = message.text.strip()
        if password != p2:
            self.bot.send_message(message.chat.id,'Пароли не совпали! Введите пароль повторно: ')
            self.bot.register_next_step_handler(message,self.get_new_password)
            return
        
        self.rec_data[message.chat.id]['new_password'] = password
        data = {"new_password":password}
        uid = self.rec_data[message.chat.id]['uid']
        token = self.rec_data[message.chat.id]['token']

        response = requests.post(f"{API_URL}password_reset_confirm/{uid}/{token}/", data)
        if response.status_code == 200:
            self.bot.send_message(message.chat.id, 'Пароль сменен успешно!')
            self.rec_data.pop(message.chat.id)
        else:
            self.bot.send_message(message.chat.id, f'Ошибка: {response.status_code} {response.text}')
            
        
        
class ChildRegister:

    def __init__(self, bot, auth):
        self.bot = bot
        self.auth = auth
        self.child_data = {}

        self.bot.callback_query_handler(func=lambda call:call.data=='cancel_register_child')(self.cancel_register)

    def cancel_register(self, call):
        self.child_data.pop(call.message.chat.id, None)
        self.bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
        self.bot.send_message(call.message.chat.id, '❌ Регистрация отменена.')

    def cancel_markup(self):
        markup=types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('❌ Отменить', callback_data='cancel_register_child'))
        return markup

    def child_register(self, call):
        chat_id = call.message.chat.id
        if not self.auth.is_authenticated(chat_id):
            self.bot.send_message(chat_id, "Вы не авторизованы. Введите /login")
            return
        
        if call.message.chat.id in self.child_data:
            self.bot.answer_callback_query(call.id, '⏳ Вы уже начали регистрацию')
            return
        
        self.child_data[call.message.chat.id] = {}

        self.bot.send_message(call.message.chat.id, 'Введите имя ребенка: ', reply_markup=self.cancel_markup())
        self.bot.register_next_step_handler(call.message, self.get_child_name)

    def get_child_name(self, message):
        if message.chat.id not in self.child_data:
            return
        
        first_name = message.text.strip()
        self.child_data[message.chat.id]['first_name'] = first_name

        self.bot.send_message(message.chat.id, 'Введите фамилию', reply_markup=self.cancel_markup())
        self.bot.register_next_step_handler(message, self.get_child_last_name)

    def get_child_last_name(self, message):
        if message.chat.id not in self.child_data:
            return
        last_name = message.text.strip()
        chat_id = message.chat.id
        self.child_data[chat_id]['last_name'] = last_name

        data={
            'first_name':self.child_data[chat_id]['first_name'],
            'last_name':self.child_data[chat_id]['last_name'],
            'parent':self.auth.sessions[chat_id]['user']['id'],
            'role':'child'
        }
        
        try:
            response=self.auth.post(chat_id, "account/child_register/", data)
            if response.status_code in [200, 201]:
                self.bot.send_message(chat_id, f"✅ Ребёнок, {self.child_data[chat_id]['last_name']} {self.child_data[chat_id]['first_name']}, зарегистрирован! ")
            else:
                self.bot.send_message(chat_id, f'Ошибка при регистрации: {response.status_code}\n{response.text}')
        except Exception as e:
            self.bot.send_message(chat_id,f"Произошла ошибка при регистрации: {e}")
        finally:
            self.child_data.pop(chat_id)




    
        

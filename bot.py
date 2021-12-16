import sqlite3
import telebot
import config
import hashlib
from logging import NullHandler, fatal
from telebot import types
from newsapi import NewsApiClient
from requests.models import Response

bot = telebot.TeleBot(config.TOKEN)
conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

password=''
log=''

# news API

newsapi= NewsApiClient(api_key=config.API)

def get_news(categ):
       data = newsapi.get_top_headlines(category = categ, language='en', page_size=3)
       articles = data['articles']
       news=[]
       for x,y in enumerate(articles):

              text=(f"{articles[x]['title']}\n\n{articles[x]['description']}\n\nURL: {articles[x]['url']}\n")       
              news.append(text)
              
       return news



# БД

# регистрация
def db_table_reg(message):
    cursor.execute(f"SELECT id FROM users WHERE login = '{log}'").fetchone()
    conn.commit()
    if cursor.fetchone() is None:
        id = message.chat.id
        cursor.execute(f'INSERT INTO users (id,login,password) VALUES (?,?,?)', (id,log,password))
        conn.commit()
        bot.send_message(message.chat.id, 'Готово, вы зарегестрированы !'.format(message.from_user,bot.get_me()),parse_mode = "html")
    else:
        bot.send_message(message.chat.id, 'Данный Login занят, придумайте другой'.format(message.from_user,bot.get_me()),parse_mode = "html")
        reggistrat(message)


# вход
def db_table_log(message):
    if cursor.execute(f"SELECT id FROM users WHERE login = '{log}'").fetchone() is None:
        bot.send_message(message.chat.id, 'Такого пользователея нет, зарегестрируйтесь'.format(message.from_user,bot.get_me()),parse_mode = "html")
    else:
        cursor.execute(f"SELECT id FROM users WHERE login = '{log}' AND password='{password}'")
        conn.commit()
        if cursor.fetchone() is None:
            bot.send_message(message.chat.id, 'Неправильный логин или пароль !'.format(message.from_user,bot.get_me()),parse_mode = "html")
        else:
            k1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("/help")
            item2 = types.KeyboardButton("/news")
            item3 = types.KeyboardButton("/game")
            item4 = types.KeyboardButton("/exit")
            k1.add(item1,item2,item3,item4)

            bot.send_message(message.chat.id, 'Вы вошли!'.format(message.from_user,bot.get_me()),parse_mode = "html",reply_markup = k1)
            id = message.chat.id
            cursor.execute(f'INSERT INTO user_online (id_user) VALUES ({id})')
            conn.commit()


# проверка на вход
def logUser(message):

    cursor.execute(f"SELECT id_user FROM user_online WHERE id_user = '{message.chat.id}'")
    conn.commit()
    if cursor.fetchall() == []:
        return True
    else:
        return False



# функции

# регистрация
def get_login_reg(message):
    global log
    log = hashlib.md5(message.text.encode()).hexdigest()

    bot.send_message(message.chat.id, 'Password :'.format(message.from_user,bot.get_me()),parse_mode = "html")
    bot.register_next_step_handler(message,get_password_reg)

def get_password_reg(message):
    global password
    password = hashlib.md5(message.text.encode()).hexdigest()
    db_table_reg(message)



# вход
def get_login_log(message):
    global log
    log = hashlib.md5(message.text.encode()).hexdigest()

    bot.send_message(message.chat.id, 'Password :'.format(message.from_user,bot.get_me()),parse_mode = "html")
    bot.register_next_step_handler(message,get_password_log)

def get_password_log(message):
    global password
    password = hashlib.md5(message.text.encode()).hexdigest()
    db_table_log(message)



# выход
def exit_log(message):
    global password
    global log
    password = ""
    log = ""

    id = message.chat.id
    cursor.execute(f"DELETE FROM user_online WHERE id_user = {id} ").fetchone()
    conn.commit()

    k1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("/help")
    item2 = types.KeyboardButton("/registration")
    item3 = types.KeyboardButton("/login")
    item4 = types.KeyboardButton("/game")
    k1.add(item1,item2,item3,item4)
    bot.send_message(message.chat.id, 'Вы вышли из аккаунта'.format(message.from_user,bot.get_me()),parse_mode = "html",reply_markup = k1)



# бот

# старт
@bot.message_handler(commands = ['start'])  
def welcome(message):

    k1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("/help")
    item2 = types.KeyboardButton("/registration")
    item3 = types.KeyboardButton("/login")
    item4 = types.KeyboardButton("/game")
    k1.add(item1,item2,item3,item4)

    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEDBrBhXXKdn-N28Yke4lx8iDWJv8xWlAAC5AMAAonq5Qf3qStRjjmNnyEE')
    bot.send_message(message.chat.id,"Хаай, {0.first_name} {0.last_name}".format(message.from_user,bot.get_me()),
    parse_mode = "html",reply_markup = k1)



# региистрация
@bot.message_handler(commands = ['registration'])
def reggistrat(message):

    bot.send_message(message.chat.id, 'Регистрация пользователя'.format(message.from_user,bot.get_me()),parse_mode = "html")
    bot.send_message(message.chat.id, 'Login :'.format(message.from_user,bot.get_me()),parse_mode = "html")
    bot.register_next_step_handler(message,get_login_reg)



# вход
@bot.message_handler(commands = ['login'])
def login(message):
    logUser(message)
    if logUser(message) == True:
        bot.send_message(message.chat.id, 'Вход'.format(message.from_user,bot.get_me()),parse_mode = "html")
        bot.send_message(message.chat.id, 'Login :'.format(message.from_user,bot.get_me()),parse_mode = "html")
        bot.register_next_step_handler(message,get_login_log)
    else:
        bot.send_message(message.chat.id, 'Вы уже вошли в аккаунт'.format(message.from_user,bot.get_me()),parse_mode = "html")



# выход
@bot.message_handler(commands = ['exit'])
def exit(message):
    exit_log(message)



# вызов новостей
@bot.message_handler(commands = ['news'])
def games(message):

    if logUser(message) == False:
        keyboardNews = types.InlineKeyboardMarkup()
        entertainmentK = types.InlineKeyboardButton(text = 'Entertainment', callback_data = 'entertainment')
        keyboardNews.add(entertainmentK)

        generalK = types.InlineKeyboardButton(text = 'General', callback_data = 'general')
        keyboardNews.add(generalK)

        healthK = types.InlineKeyboardButton(text = 'Health', callback_data = 'health')
        keyboardNews.add(healthK)

        scienceK = types.InlineKeyboardButton(text = 'Science', callback_data = 'science')
        keyboardNews.add(scienceK)

        sportsK = types.InlineKeyboardButton(text = 'Sports', callback_data = 'sports')
        keyboardNews.add(sportsK)

        technologyK = types.InlineKeyboardButton(text = 'Technology', callback_data = 'technology')
        keyboardNews.add(technologyK)

        bot.send_message(message.chat.id,"Выберите категорию новостей :".format(message.from_user,bot.get_me()),
        parse_mode = "html",reply_markup = keyboardNews)

    else:
        bot.send_message(message.chat.id,"Вы не вошли в аккаунт !".format(message.from_user,bot.get_me()),parse_mode = "html")
 


# обработка кнопок новостей
@bot.callback_query_handler(func = lambda call: True)
def callback_news(call):
    if call.data != None:
        if call.data=="entertainment" or call.data=="general" or call.data=="health" or call.data=="science" or call.data=="sports" or call.data=="technology":
            for x in get_news(categ=call.data):  
                bot.send_message(call.message.chat.id, {x})
        if call.data == "game1":
            bot.send_message(call.message.chat.id, 'https://telegram.me/gamebot?game=Corsairs')
        if call.data == "game2":
            bot.send_message(call.message.chat.id, 'https://telegram.me/gamebot?game=Lumberjack')
        if call.data == "game3":
            bot.send_message(call.message.chat.id, 'https://telegram.me/gamebot?game=MathBattle')
    else:
        bot.send_message(call.message.chat.id, "Ошибка")



# игры
@bot.message_handler(commands = ['game'])
def games(message):
    keyboardGame = types.InlineKeyboardMarkup()

    game1 = types.InlineKeyboardButton(text = 'Corsairs', callback_data = 'game1')
    keyboardGame.add(game1)

    game2 = types.InlineKeyboardButton(text = 'Lumberjack', callback_data = 'game2')
    keyboardGame.add(game2)

    game3 = types.InlineKeyboardButton(text = 'MathBattle', callback_data = 'game3')
    keyboardGame.add(game3)

    bot.send_message(message.chat.id,"Выберите игру из списка :".format(message.from_user,bot.get_me()),
    parse_mode = "html",reply_markup = keyboardGame)



# help
@bot.message_handler(commands=['help'])  
def help_command(message):  
    keyboard = telebot.types.InlineKeyboardMarkup()  
    bot.send_message(  
        message.chat.id,
        'Данный бот предоставляет свежие новости и не только\n' +
        'Для того что бы получать новости необходимо зарегестрироватсья или войти в аккаунт \n' +
        'Регистрация - /registration \n' +
        'Вход - /login \n' +
        'Выход - /exit \n'+
        'После входа в аккаунт вам достурны свежие новости с выбором категории \n'+
        'Новости - /news \n'+
        '````````````````````````````````````````````````````````\n'+
        'Доп. функции: \n'+
        'Распознание слов: привет; пока; мда; ныа \n'+
        'Игры для чатика - /game \n',
        reply_markup=keyboard
    )


# url
@bot.message_handler(commands=['url'])  
def url(message):  
    if logUser(message) == False:
        bot.send_message(message.chat.id,"URL-сокращатель\nВыберете тип приватности".format(message.from_user,bot.get_me()),parse_mode = "html")
    else:
        bot.send_message(message.chat.id,"Вы не вошли в аккаунт !".format(message.from_user,bot.get_me()),parse_mode = "html")




# обработка слов
@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, 'Hi')
    elif  message.text.lower() == 'пока':
        bot.send_message(message.chat.id, 'Bye')
    elif message.text.lower() == 'мда':
        bot.send_message(message.chat.id, 'Мдээээкалка')
    elif message.text.lower() == 'ныа':
        bot.send_sticker(message.chat.id, 'CAACAgQAAxkBAAEDByphXZaAXoCWk5pih9bdUksIGbiBPwACNwEAAqghIQYMfziKQlkdXyEE')
    else :
        bot.send_message(message.chat.id, 'Я вас не понимаю (')   
   


bot.polling(non_stop=True)
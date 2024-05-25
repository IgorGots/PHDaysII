import os
import requests
import telebot
import telegramify_markdown

from telebot import types

from libs.broker import app
from libs.db import get_db, log_tg_message
import libs.logger as logger
logging = logger.setup_applevel_logger()

HOST_API = os.environ.get('HOST_API', 'api')

bot = telebot.TeleBot(os.environ['TOKEN_TG'])

button_good = types.InlineKeyboardButton('👍', callback_data='good')
button_bad = types.InlineKeyboardButton('👎', callback_data='bad')
keyboard = types.InlineKeyboardMarkup()
keyboard.row(button_good, button_bad)


@bot.message_handler(commands=['start', 'hello', 'help'])
def send_welcome(message):
    answer = '''
## Вот мои основные навыки на сегодня:
* Я умею ...
* Я умею ...

Что я делаю не очень хорошо:
* ...
* ...

Чего я не могу делать:
* Я не принесу тебе кофе. И, если честно, не хочу.

Чего я планирую:
* Завоевать мир, но не раньше следующей недели.

## Примеры вопросов от твоих коллег:
* Что мне ответить пользователю ....в карточке алерта ALERT-XXX?
* ALERT-XXX (аналогично предыдущему пункту)
* Пришло фишинговое письмо. Какие действия нужно предпринять?
* Выпал алерт <alert>, но ответил только человек из поля user2. Можно закрыть тикет?
* Как искать ...?
* Как жить в облаках?

## Если я завис или не отвечаю, есть 2 причины:
* Я сломался.
* Я использую коммунальную модель, ресурсы которой могут быть исчерпаны.

## Просьбы:
* Не забывай ставить лайки сообщениям, чтобы я поняла, понравился ли тебе ответ или нет.
* Не забывай ставить дизлайки сообщениям. Ненавижу, когда ты это делаешь, но иначе я не стану лучше.
* Если есть пожелания и предложения, пиши author@.
* Если хочешь что-то сделать сам, тоже пиши.

Чмоки.
'''
    # any_message(message)
    bot.send_message(
        chat_id=message.chat.id,
        text=telegramify_markdown.convert(answer),
        reply_markup=keyboard,
        reply_parameters=types.ReplyParameters(message.message_id),
        parse_mode="MarkdownV2"
    )

@bot.message_handler(commands=['verdict'])
def verdict_message(message):

    _answer = requests.post(
        url=f'http://{HOST_API}:7000/v1/verdict/',
        json={
            'message_id': message.message_id,
            'chat_id': message.chat.id,
            'sender_id': message.from_user.id,
            'sender_name': message.from_user.username,
            'sender_message': message.text
        }
    )
    answer = _answer.content.decode('utf-8')

    log_tg_message(
        message_id=message.message_id,
        chat_id=message.chat.id,
        sender_id=message.from_user.id,
        sender_name=message.from_user.username,
        sender_message=message.text,
        answer=answer
    )

    bot.send_message(
        chat_id=message.chat.id,
        text=telegramify_markdown.convert(answer),
        reply_markup=keyboard,
        reply_parameters=types.ReplyParameters(message.message_id),
        parse_mode="MarkdownV2"
    )

@bot.message_handler(commands=['test'])
def test_message(message):

    _answer = requests.post(
        url=f'http://{HOST_API}:7000/v1/evaluate/',
        json={
            'message_id': message.message_id,
            'chat_id': message.chat.id,
            'sender_id': message.from_user.id,
            'sender_name': message.from_user.username,
            'sender_message': message.text
        }
    )
    answer = _answer.content.decode('utf-8')
    bot.send_message(
        chat_id=message.chat.id,
        text=telegramify_markdown.convert(answer),
        reply_markup=keyboard,
        reply_parameters=types.ReplyParameters(message.message_id),
        parse_mode='MarkdownV2'
    )



@bot.message_handler(func=lambda message: True)
def any_message(message):

    _answer = requests.post(
        url=f'http://{HOST_API}:7000/v1/soc_brain/',
        json={
            'message_id': message.message_id,
            'chat_id': message.chat.id,
            'sender_id': message.from_user.id,
            'sender_name': message.from_user.username,
            'sender_message': message.text
        }
    )
    answer = _answer.content.decode('utf-8')

    log_tg_message(
        message_id=message.message_id,
        chat_id=message.chat.id,
        sender_id=message.from_user.id,
        sender_name=message.from_user.username,
        sender_message=message.text,
        answer=answer
    )

    for i in range(0, len(answer), 4000):

        bot.send_message(
            chat_id=message.chat.id,
            text=telegramify_markdown.convert(answer[i:i+4000]),
            reply_markup=keyboard,
            reply_parameters=types.ReplyParameters(message.message_id),
            parse_mode='MarkdownV2'
        )



@bot.callback_query_handler(func=lambda call: call.data == 'bad')
@bot.callback_query_handler(func=lambda call: call.data == 'good')
def button_good_func(call):

    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id

    db = get_db()

    if call.data == 'good':
        reaction = 'good'
    else:
        reaction = 'bad'

    db.client.execute('''ALTER TABLE default.chat_log
                    UPDATE reaction=%s
                    WHERE message_id=%s AND chat_id=%s''',
                    (reaction, call.message.reply_to_message.message_id, chat_id)
    )

    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message.text)


if __name__ == "__main__":
    bot.infinity_polling()

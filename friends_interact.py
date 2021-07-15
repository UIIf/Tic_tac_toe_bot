from base_functions import send_message
import sqlite3
from telebot import types


def invite_logic(bot, message):
    text = message.text.replace(' ', '')
    if text[0] == "@":
        f_req = sqlite3.connect("friend_requests.db")
        f_sql = f_req.cursor()
        f_sql.execute(
            f"""UPDATE friend_requests SET Friend_User_Name = "{text[1:]}" WHERE Chat_id = {message.chat.id}""")
        f_req.commit()
        markup_in_game = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup_in_game.add("/surrender")
        send_message(bot, message.chat.id, "Waiting for " + text[1:], markup_in_game)
    else:
        bot.send_message(message.chat.id, "Bad")

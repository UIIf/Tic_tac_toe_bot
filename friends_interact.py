from base_functions import send_message
import sqlite3
from telebot import types


def invite_logic(bot, message):
    text = message.text.replace(' ', '')
    if text[0] == "@":
        states = sqlite3.connect('Tic_tac_toe.db')
        sql = states.cursor()

        f_req = sqlite3.connect("friend_requests.db")
        f_sql = f_req.cursor()
        second_user = f_sql.execute(f"SELECT Friend_User_Name FROM friend_requests WHERE Chat_id = {message.chat.id}").fetchone()
        if second_user[0] != "":
            second_user = sql.execute(f"""SELECT Chat_id FROM players_state WHERE UserName = "{second_user[0]}" """).fetchone()
            if not (second_user is None):
                bot.send_message(second_user[0], "Someone cancel your invitation")
        f_sql.execute(
            f"""UPDATE friend_requests SET Friend_User_Name = "{text[1:]}" WHERE Chat_id = {message.chat.id}""")
        f_req.commit()
        markup_in_game = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup_in_game.add("/surrender")
        send_message(bot, message.chat.id, "Waiting for " + text[1:], markup_in_game)

        second_user = sql.execute(f"""SELECT Chat_id FROM players_state WHERE UserName = "{text[1:]}" """).fetchone()
        if not (second_user is None):
            bot.send_message(second_user[0], "Someone invites you")
    else:
        bot.send_message(message.chat.id, "Bad")

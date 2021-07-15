from telebot import types
import sqlite3
from enum import Enum


class PlayerState(Enum):
    WAIT = 0
    PLAY_WITH_BOT = 1
    PLAY_LOCAL = 2
    PLAY_WITH_PLAYER = 3
    WAIT_FRIEND = 4


class BotGameStates(Enum):
    WAIT_MOVE = 0
    CHOOSE_SIDE = 1


def set_player_state(chat_id, state):
    states = sqlite3.connect('Tic_tac_toe.db')
    sql = states.cursor()
    sql.execute(f"UPDATE players_state SET Current_State = {state.value} WHERE Chat_id = {chat_id}")
    states.commit()
    del states


def win_chek(field):
    win = "0"
    for index in range(3):
        if(field[index] == field[index+3]) and (field[index] == field[index + 6] and (field[index] != "0")):
            win = field[index]
            break
        if(field[index*3] == field[index*3 + 1]) and (field[index*3] == field[index*3 + 2] and (field[index*3] != "0")):
            win = field[index*3]

    if win == "0":
        if(field[0] == field[4]) and (field[0] == field[8]):
            win = field[0]
        elif(field[2] == field[4]) and (field[2] == field[6]):
            win = field[2]
    return win


def free_steps(field):
    free = 0
    for i in field:
        if i == "0":
            free += 1
    return free


def generate_field_and_keyboard(field):
    markup_in_game = types.ReplyKeyboardMarkup(one_time_keyboard=True)

    output = ""
    buttons = [["1", "2", "3"],
               ["4", "5", "6"],
               ["7", "8", "9"]]
    for i in range(9):
        if i % 3 == 0:
            output += "\n"
        # elif i != 0:
        #     output += "|"

        if field[i] == "1":
            output += "❌"
            buttons[i // 3][i % 3] = " "
        elif field[i] == "2":
            output += "⭕️"
            buttons[i // 3][i % 3] = " "
        else:
            output += "⬜️"

    for i in range(3):
        markup_in_game.add(buttons[i][0], buttons[i][1], buttons[i][2])

    markup_in_game.add("/surrender")
    return [output, markup_in_game]


def send_message(bot, chat_id, text, markup_in_game=types.ReplyKeyboardRemove()):
    bot.send_message(chat_id, text, reply_markup=markup_in_game)


def player_step(bot, chat_id, field, symbol, num):
    field = field.split(" ")
    fin = None
    if field[num-1] != "0":
        bot.send_message(bot, chat_id, "Pleas use keyboard")
    else:
        field[num-1] = symbol
        # fin = win_chek(field)
        # if fin == symbol:
        #     if bd == "bot_games":
        #         text = "You win\n" + generate_field_and_keyboard(field)[0]
        #     else:
        #         if symbol == "1":
        #             symbol = "❌"
        #         else:
        #             symbol = "⭕️"
        #         text = symbol + " win\n" + generate_field_and_keyboard(field)[0]
        #     games_sql.execute(f"DELETE FROM {bd} WHERE Chat_id = {chat_id}")
        #     games.commit()
        #     send_message(bot, chat_id, text)
        #     set_player_state(chat_id, PlayerState.WAIT)
        #     # return fin
        # else:
        #     text_field = " ".join(field)
        #     games_sql.execute(f"""UPDATE {bd} SET Game_field = "{text_field}" WHERE Chat_id = {chat_id} """)
        #     free = 0
        #     for i in field:
        #         if i == "0":
        #             free += 1
        #     if free > 0:
        #         pass
        #     else:
        #         fin = None
        #         text = "Tie\n" + generate_field_and_keyboard(field)[0]
        #         games_sql.execute(f"DELETE FROM {bd} WHERE Chat_id = {chat_id}")
        #         send_message(bot, chat_id, text)
        #         set_player_state(chat_id, PlayerState.WAIT)
        #         # return fin
    return field
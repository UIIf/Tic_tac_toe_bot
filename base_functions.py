from telebot import types
import sqlite3


class PlayerState:
    WAIT = 0
    PLAY_WITH_BOT = 1
    PLAY_LOCAL = 2
    PLAY_WITH_PLAYER = 3
    WAIT_FRIEND = 4


class BotGameStates:
    WAIT_MOVE = 0
    CHOOSE_SIDE = 1


class MpGameStates:
    WAIT_MOVE_F = 0
    WAIT_MOVE_S = 1
    WAIT_REMATCH = 2


class Send_Messages_Both:
    FOR_FIRST = 0
    FOR_SECOND = 1
    FOR_BOTH = 2


def set_player_state(chat_id, state):
    states = sqlite3.connect('Tic_tac_toe.db')
    sql = states.cursor()
    sql.execute(f"UPDATE players_state SET Current_State = {state} WHERE Chat_id = {chat_id}")
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


def send_massage_both(bot, chat_id_f, chat_id_s, text, state=-1, markup_in_game=types.ReplyKeyboardRemove(), additional_text=""):
    if state == Send_Messages_Both.FOR_FIRST:
        bot.send_message(chat_id_f, additional_text+text, reply_markup=markup_in_game)
        bot.send_message(chat_id_s, text, types.ReplyKeyboardRemove())
    elif state == Send_Messages_Both.FOR_SECOND:
        bot.send_message(chat_id_f, text, types.ReplyKeyboardRemove())
        bot.send_message(chat_id_s, additional_text+text, reply_markup=markup_in_game)
    elif state == Send_Messages_Both.FOR_BOTH:
        bot.send_message(chat_id_f, additional_text+text, reply_markup=markup_in_game)
        bot.send_message(chat_id_s, additional_text+text, reply_markup=markup_in_game)
    else:
        bot.send_message(chat_id_f, text, types.ReplyKeyboardRemove())
        bot.send_message(chat_id_s, text, types.ReplyKeyboardRemove())


def player_step(field, symbol, num):
    field = field.split(" ")
    if field[num - 1] == "0":
        field[num-1] = symbol
        return field
    return None
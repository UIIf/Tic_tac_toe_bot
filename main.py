import random

import telebot
from telebot import types
import sqlite3
from enum import Enum

# token = ""
from config import *


class PlayerState(Enum):
    WAIT = 0
    PLAY_WITH_BOT = 1
    PLAY_LOCAL = 2
    PLAY_WITH_PLAYER = 3
    WAIT_FRIEND = 4


class BotGameStates(Enum):
    WAIT_MOVE = 0
    CHOOSE_SIDE = 1


p_state = sqlite3.connect('Tic_tac_toe.db')
p_sql = p_state.cursor()

p_sql.execute("""CREATE TABLE IF NOT EXISTS players_state(
    Chat_id INTEGER,
    Name TEXT,
    Current_State INTEGER);
""")

p_state.commit()
del p_state

g_bot = sqlite3.connect('bot_games.db')
g_sql = g_bot.cursor()

g_sql.execute("""CREATE TABLE IF NOT EXISTS bot_games(
    Chat_id INTEGER,
    Game_State INTEGER,
    Game_field TEXT,
    Bot_Symbol TEXT);
""")
g_bot.commit()
del g_bot

l_games = sqlite3.connect('local_games.db')
l_sql = l_games.cursor()
l_sql.execute("""CREATE TABLE IF NOT  EXISTS local_games(
    Chat_id INTEGER,
    Game_field TEXT,
    Current_Symbol TEXT);""")
l_games.commit()

del l_games

current_users = []
is_adding = False
bot = telebot.TeleBot(token)


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


def player_step(chat_id, field, symbol, num, games, games_sql, bd):
    field = field.split(" ")
    fin = None
    if field[num-1] != "0":
        bot.send_message(chat_id, "Pleas use keyboard")
    else:
        field[num-1] = symbol
        fin = win_chek(field)
        if fin == symbol:
            if bd == "bot_games":
                text = "You win\n" + generate_field_and_keyboard(field)[0]
            else:
                if symbol == "1":
                    symbol = "❌"
                else:
                    symbol = "⭕️"
                text = symbol + " win\n" + generate_field_and_keyboard(field)[0]
            games_sql.execute(f"DELETE FROM {bd} WHERE Chat_id = {chat_id}")
            games.commit()
            send_message(chat_id, text)
            set_player_state(chat_id, PlayerState.WAIT)
            return fin
        else:
            text_field = " ".join(field)
            games_sql.execute(f"""UPDATE {bd} SET Game_field = "{text_field}" WHERE Chat_id = {chat_id} """)
            free = 0
            for i in field:
                if i == "0":
                    free += 1
            if free > 0:
                pass
            else:
                fin = None
                text = "Tie\n" + generate_field_and_keyboard(field)[0]
                games_sql.execute(f"DELETE FROM {bd} WHERE Chat_id = {chat_id}")
                send_message(chat_id, text)
                set_player_state(chat_id, PlayerState.WAIT)
                return fin
    if bd != "bot_games":
        msg = generate_field_and_keyboard(field)
        send_message(chat_id, msg[0], msg[1])
        print(0)
    games.commit()
    return fin


def bot_step(current_game, games, games_sql):
    chat_id = current_game[0]
    field = current_game[2].split(" ")
    opponent_symbol = "1"
    symbol = current_game[3]
    if symbol != "2":
        symbol = "1"
        opponent_symbol = "2"
    possible_moves = []
    next_step = None
    win = False
    for i in range(9):
        if field[i] == "0":
            possible_moves.append(i)
            field[i] = symbol
            if win_chek(field) != "0":
                next_step = i
                win = True
            if not win:
                field[i] = opponent_symbol
                if win_chek(field) != "0":
                    next_step = i
            field[i] = "0"

    if (next_step is None) or (not win):
        if next_step is None:
            next_step = random.choice(possible_moves)

        field[next_step] = symbol

        if len(possible_moves) < 2:
            text = "Tie\n" + generate_field_and_keyboard(field)[0]
            games_sql.execute(f"DELETE FROM bot_games WHERE Chat_id = {chat_id}")
            send_message(chat_id, text)
            set_player_state(chat_id, PlayerState.WAIT)
        else:
            txt_field = ' '.join(field)
            games_sql.execute(f"""UPDATE bot_games SET Game_field = "{txt_field}" WHERE Chat_id = {chat_id} """)
            msg = generate_field_and_keyboard(field)
            send_message(chat_id, msg[0], msg[1])
    else:
        field[next_step] = symbol
        text = "You lose\n" + generate_field_and_keyboard(field)[0]
        games_sql.execute(f"DELETE FROM bot_games WHERE Chat_id = {chat_id}")
        send_message(chat_id, text)
        set_player_state(chat_id, PlayerState.WAIT)

    games.commit()


def check_reg(states, sql, message):
    sql.execute(f"SELECT * FROM players_state WHERE Chat_id = {message.chat.id}")
    if sql.fetchone() is None:
        sql.execute(f"INSERT INTO players_state VALUES (?,?,?)", (message.chat.id, message.from_user.first_name, 0))
        states.commit()


def versus_bot_logic(message):
    games = sqlite3.connect('bot_games.db')
    games_sql = games.cursor()
    current_game = games_sql.execute(f"SELECT * FROM bot_games WHERE Chat_id = {message.chat.id}").fetchone()
    if current_game[1] == BotGameStates.CHOOSE_SIDE.value:
        if message.text == "⭕️.":
            games_sql.execute(f"""UPDATE bot_games SET Bot_Symbol = "{1}" WHERE Chat_id = {message.chat.id}""")
            bot_step(games_sql.execute(f"SELECT * FROM bot_games WHERE Chat_id = {message.chat.id}").fetchone(), games,
                     games_sql)
        elif message.text != "❌.":
            bot.send_message(message.chat.id, "Pls use keyboard")
            return
        else:
            msg = generate_field_and_keyboard(["0", "0", "0", "0", "0", "0", "0", "0", "0"])
            send_message(message.chat.id, msg[0], msg[1])
        games_sql.execute(f"UPDATE bot_games SET Game_State = {BotGameStates.WAIT_MOVE.value} WHERE Chat_id = {message.chat.id}")
        games.commit()
    else:
        try:
            temp = int(message.text)
            if (temp > 0) and (temp < 10):
                player_symbol = current_game[3]
                if player_symbol == "1":
                    player_symbol = "2"
                else:
                    player_symbol = "1"
                player_response = player_step(current_game[0], current_game[2], player_symbol, temp, games, games_sql)
                if not(player_response is None):
                    if player_response == "0":
                        current_game = games_sql.execute(f"SELECT * FROM bot_games WHERE Chat_id = {message.chat.id}").fetchone()
                        bot_step(current_game, games, games_sql)
        except ValueError:
            bot.send_message(message.chat.id, "Smth go wrong")


def local_logic(message):
    games = sqlite3.connect('local_games.db')
    games_sql = games.cursor()
    try:
        temp = int(message.text)
        current_game = games_sql.execute(f"SELECT * FROM local_games WHERE Chat_id = {message.chat.id}").fetchone()
        if (temp > 0) and (temp < 10):
            player_step(current_game[0], current_game[1], current_game[2], temp, games, games_sql, "local_games")
            symbol = "1"
            if current_game[2] == "1":
                symbol = "2"
            games_sql.execute(f"UPDATE local_games SET Current_Symbol = {symbol} WHERE Chat_id = {message.chat.id}")
            games.commit()
    except ValueError:
        bot.send_message(message.chat.id, "Smth go wrong")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    states = sqlite3.connect('Tic_tac_toe.db')
    sql = states.cursor()
    bot.send_message(message.chat.id, "Simple bot, for playing tic-tac-toe with strangers")
    sql.execute(f"SELECT Chat_id FROM players_state WHERE Chat_id = {message.chat.id}")
    check_reg(states, sql, message)
    del states


@bot.message_handler(commands=['play_bot'])
def play_with_bot(message):
    global is_adding
    while is_adding:
        pass
    if not(message.chat.id in current_users):

        is_adding = True
        current_users.append(message.chat.id)
        is_adding = False

        states = sqlite3.connect('Tic_tac_toe.db')
        sql = states.cursor()
        check_reg(states, sql, message)
        if sql.execute(f"SELECT Current_State FROM players_state WHERE Chat_id = {message.chat.id}").fetchone()[0] == PlayerState.WAIT.value:
            sql.execute(f"UPDATE players_state SET Current_State = {PlayerState.PLAY_WITH_BOT.value} WHERE Chat_id = {message.chat.id}")
            states.commit()
            games = sqlite3.connect('bot_games.db')
            games_sql = games.cursor()
            games_sql.execute(f"INSERT INTO bot_games VALUES (?, ?, ?, ?)", (message.chat.id, BotGameStates.CHOOSE_SIDE.value, "0 0 0 0 0 0 0 0 0", "2"))
            games.commit()
            del games
            markup_in_game = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup_in_game.add("❌.", "⭕️.")
            send_message(message.chat.id, "Choose your symbol", markup_in_game)
        else:
            bot.send_message(message.chat.id, "U must finish ur game")
        del states
        current_users.remove(message.chat.id)


@bot.message_handler(commands=['play_local'])
def play_local(message):
    global is_adding
    while is_adding:
        pass
    if not(message.chat.id in current_users):

        is_adding = True
        current_users.append(message.chat.id)
        is_adding = False

        states = sqlite3.connect('Tic_tac_toe.db')
        sql = states.cursor()
        check_reg(states, sql, message)
        if sql.execute(f"SELECT Current_State FROM players_state WHERE Chat_id = {message.chat.id}").fetchone()[0] == PlayerState.WAIT.value:
            sql.execute(f"UPDATE players_state SET Current_State = {PlayerState.PLAY_LOCAL.value} WHERE Chat_id = {message.chat.id}")
            states.commit()
            games = sqlite3.connect('local_games.db')
            games_sql = games.cursor()
            games_sql.execute(f"INSERT INTO local_games VALUES (?, ?, ?)", (message.chat.id, "0 0 0 0 0 0 0 0 0", "2"))
            games.commit()
            del games
            msg = generate_field_and_keyboard(["0", "0", "0", "0", "0", "0", "0", "0", "0"])
            send_message(message.chat.id, msg[0], msg[1])
        else:
            bot.send_message(message.chat.id, "U must finish ur game")
        del states
        current_users.remove(message.chat.id)


@bot.message_handler(commands=['where_am_i'])
def where_am_i(message):
    states = sqlite3.connect('Tic_tac_toe.db')
    sql = states.cursor()
    player = sql.execute(f"SELECT * FROM players_state WHERE Chat_id = {message.chat.id}").fetchone()
    answer = "ERROR"
    if player is None:
        answer = """You are currently not registered, start playing or write "/start" for registration."""
    else:
        player_state = player[2]
        if player_state == PlayerState.WAIT.value:
            answer = "You are currently sitting in lobby."
        elif player_state == PlayerState.PLAY_WITH_BOT.value:
            answer = "You are currently playing with bot."
        elif player_state == PlayerState.PLAY_WITH_PLAYER.value:
            answer = "You are currently playing with other user."
        elif player_state == PlayerState.WAIT_FRIEND.value:
            answer = "You are currently waiting your friend."
    bot.reply_to(message, answer)
    del states


@bot.message_handler(commands=['surrender'])
def surrender(message):
    states = sqlite3.connect('Tic_tac_toe.db')
    sql = states.cursor()
    check_reg(states, sql, message)
    player = sql.execute(f"SELECT Current_State FROM players_state WHERE Chat_id = {message.chat.id}").fetchone()
    if player[0] == PlayerState.PLAY_WITH_BOT.value:
        sql.execute(f"UPDATE players_state SET Current_State = {PlayerState.WAIT.value} WHERE Chat_id = {message.chat.id}")
        states.commit()
        games = sqlite3.connect('bot_games.db')
        games_sql = games.cursor()
        games_sql.execute(f"DELETE FROM bot_games WHERE Chat_id = {message.chat.id}")
        games.commit()
        del games
    del states


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global is_adding
    while is_adding:
        pass
    if not(message.chat.id in current_users):

        is_adding = True
        current_users.append(message.chat.id)
        is_adding = False

        states = sqlite3.connect('Tic_tac_toe.db')
        sql = states.cursor()
        player = sql.execute(f"SELECT Current_State FROM players_state WHERE Chat_id = {message.chat.id}").fetchone()
        if player[0] == PlayerState.PLAY_WITH_BOT.value:
            versus_bot_logic(message)
        elif player[0] == PlayerState.PLAY_LOCAL.value:
            local_logic(message)

        current_users.remove(message.chat.id)


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


def send_message(chat_id, text, markup_in_game=types.ReplyKeyboardRemove()):
    bot.send_message(chat_id, text, reply_markup=markup_in_game)


bot.polling(none_stop=True)

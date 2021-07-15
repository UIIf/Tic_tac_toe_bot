import random

import telebot
from telebot import types

# token = ""
from config import *

from base_functions import PlayerState, BotGameStates, MpGameStates, SendMessagesBoth, send_message, send_massage_both, set_player_state, generate_field_and_keyboard
from bd_generator import *
from bot_game import versus_bot_logic
from local_game import local_logic
from friends_interact import invite_logic
from multiplayer import multiplayer_logic


current_users = []
is_adding = False
bot = telebot.TeleBot(token)
searching_players = None


def check_reg(states_bd, states_sql, message):
    states_sql.execute(f"""SELECT * FROM players_state WHERE UserName = "{message.from_user.username}" """)
    if states_sql.fetchone() is None:
        states_sql.execute(f"INSERT INTO players_state VALUES (?,?,?)", (message.chat.id, message.from_user.username, 0))
    else:
        states_sql.execute(
            f"""UPDATE players_state SET Chat_id = {message.chat.id} WHERE UserName = "{message.from_user.username}" """)
    states_bd.commit()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    states = sqlite3.connect('Tic_tac_toe.db')
    sql = states.cursor()
    bot.send_message(message.chat.id, "Simple bot, for playing tic-tac-toe with strangers")
    sql.execute(f"SELECT Chat_id FROM players_state WHERE Chat_id = {message.chat.id}")
    check_reg(states, sql, message)
    del states


@bot.message_handler(commands=['repository'])
def send_repository(message):
    markup = types.InlineKeyboardMarkup()
    btn_docs = types.InlineKeyboardButton(text='Link to repository', url='https://github.com/UIIf/Tic_tac_toe_bot')
    markup.add(btn_docs)
    bot.send_message(message.chat.id, "🤖 Uiif Github Repository 🤖", reply_markup=markup)


@bot.message_handler(commands=['play_bot'])
def play_with_bot(message):
    global is_adding
    while is_adding:
        pass
    if not(message.chat.id in current_users):

        is_adding = True
        current_users.append(message.chat.id)
        is_adding = False

        states_bd = sqlite3.connect('Tic_tac_toe.db')
        states_sql = states_bd.cursor()
        check_reg(states_bd, states_sql, message)

        # if current player don't play at this moment
        if states_sql.execute(f"SELECT Current_State FROM players_state WHERE Chat_id = {message.chat.id}").fetchone()[0] == PlayerState.WAIT:
            # Change player state
            states_sql.execute(f"UPDATE players_state SET Current_State = {PlayerState.PLAY_WITH_BOT} WHERE Chat_id = {message.chat.id}")
            states_bd.commit()

            # Create new game with bot
            games = sqlite3.connect('bot_games.db')
            games_sql = games.cursor()
            games_sql.execute(f"INSERT INTO bot_games VALUES (?, ?, ?, ?)", (message.chat.id, "0 0 0 0 0 0 0 0 0", "2", BotGameStates.CHOOSE_SIDE))
            games.commit()

            # Send keyboard for symbol choosing
            markup_in_game = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup_in_game.add("❌.", "⭕️.")
            send_message(bot, message.chat.id, "Choose your symbol", markup_in_game)

        else:
            bot.send_message(message.chat.id, "U must finish ur game")
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
        if sql.execute(f"SELECT Current_State FROM players_state WHERE Chat_id = {message.chat.id}").fetchone()[0] == PlayerState.WAIT:
            sql.execute(f"UPDATE players_state SET Current_State = {PlayerState.PLAY_LOCAL} WHERE Chat_id = {message.chat.id}")
            states.commit()
            games = sqlite3.connect('local_games.db')
            games_sql = games.cursor()
            games_sql.execute(f"INSERT INTO local_games VALUES (?, ?, ?)", (message.chat.id, "0 0 0 0 0 0 0 0 0", "1"))
            games.commit()
            del games
            msg = generate_field_and_keyboard(["0", "0", "0", "0", "0", "0", "0", "0", "0"])
            send_message(bot, message.chat.id, msg[0], msg[1])
        else:
            bot.send_message(bot, message.chat.id, "U must finish ur game")
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
        if player_state == PlayerState.WAIT:
            answer = "You are currently sitting in lobby."
        elif player_state == PlayerState.PLAY_WITH_BOT:
            answer = "You are currently playing with bot."
        elif player_state == PlayerState.PLAY_LOCAL:
            answer = "You are currently playing with other user local."
        elif player_state == PlayerState.WAIT_FRIEND:
            answer = "You are currently waiting your friend."
    bot.reply_to(message, answer)
    del states


@bot.message_handler(commands=['invite'])
def invite_friend(message):
    states = sqlite3.connect('Tic_tac_toe.db')
    sql = states.cursor()
    check_reg(states, sql, message)
    player = sql.execute(f"SELECT * FROM players_state WHERE Chat_id = {message.chat.id}").fetchone()
    if player[2] == PlayerState.WAIT:
        f_req = sqlite3.connect("friend_requests.db")
        f_sql = f_req.cursor()
        f_sql.execute("INSERT INTO friend_requests VALUES (?,?)", (message.chat.id, ""))
        f_req.commit()
        set_player_state(message.chat.id, PlayerState.WAIT_FRIEND)
        markup_in_game = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup_in_game.add("/surrender")
        send_message(bot, message.chat.id, "Send your friend @username", markup_in_game)
    elif player[2] == PlayerState.WAIT_FRIEND:
        bot.send_message(message.chat.id, "Wait ur friends")
    else:
        bot.send_message(message.chat.id, "U must finish ur game")


@bot.message_handler(commands=['find_random'])
def find_random(message):
    states = sqlite3.connect('Tic_tac_toe.db')
    sql = states.cursor()
    check_reg(states, sql, message)
    player = sql.execute(f"SELECT * FROM players_state WHERE Chat_id = {message.chat.id}").fetchone()
    if player[2] == PlayerState.WAIT:
        global searching_players
        if searching_players is None:
            searching_players = message.chat.id
            markup_in_game = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup_in_game.add("/surrender")
            send_message(bot, message.chat.id, "Waiting others", markup_in_game)
            set_player_state(message.chat.id, PlayerState.WAIT_RANDOM)
        elif searching_players != message.chat.id:
            mp_games = sqlite3.connect("multiplayer_games.db")
            mp_sql = mp_games.cursor()
            set_player_state(message.chat.id, PlayerState.PLAY_WITH_PLAYER)
            set_player_state(searching_players, PlayerState.PLAY_WITH_PLAYER)
            mp_sql.execute("""INSERT INTO multiplayer_games VALUES (?, ?, ?, ?)""", (searching_players, message.chat.id, "0 0 0 0 0 0 0 0 0", MpGameStates.WAIT_MOVE_F))
            msg = generate_field_and_keyboard(["0", "0", "0", "0", "0", "0", "0", "0", "0"])
            send_massage_both(bot, searching_players, message.chat.id, msg[0], SendMessagesBoth.FOR_FIRST, msg[1], "Yor turn\n")
            mp_games.commit()
            searching_players = None
    elif player[2] == PlayerState.WAIT_FRIEND:
        bot.send_message(message.chat.id, "Wait ur friends")
    else:
        bot.send_message(message.chat.id, "U must finish ur game")


@bot.message_handler(commands=['accept'])
def accept_friend(message):
    states = sqlite3.connect('Tic_tac_toe.db')
    sql = states.cursor()
    check_reg(states, sql, message)
    player = sql.execute(f"SELECT * FROM players_state WHERE Chat_id = {message.chat.id}").fetchone()
    if player[2] == PlayerState.WAIT:
        f_req = sqlite3.connect("friend_requests.db")
        f_sql = f_req.cursor()
        request = f_sql.execute(f"""SELECT Chat_id FROM friend_requests WHERE Friend_User_Name = "{message.from_user.username}" """).fetchone()
        if request is None:
            bot.send_message(message.chat.id, "No one invites u 😔")
        else:
            mp_games = sqlite3.connect("multiplayer_games.db")
            mp_sql = mp_games.cursor()
            set_player_state(message.chat.id, PlayerState.PLAY_WITH_PLAYER)
            set_player_state(request[0], PlayerState.PLAY_WITH_PLAYER)
            mp_sql.execute("""INSERT INTO multiplayer_games VALUES (?, ?, ?, ?)""", (request[0], message.chat.id, "0 0 0 0 0 0 0 0 0", MpGameStates.WAIT_MOVE_F))
            msg = generate_field_and_keyboard(["0", "0", "0", "0", "0", "0", "0", "0", "0"])
            f_sql.execute(f"DELETE FROM friend_requests WHERE Chat_id = {request[0]}")
            send_massage_both(bot, request[0], message.chat.id, msg[0], SendMessagesBoth.FOR_FIRST, msg[1], "Yor turn\n")
            mp_games.commit()
            f_req.commit()
    elif player[2] == PlayerState.WAIT_FRIEND:
        bot.send_message(message.chat.id, "Wait ur friends")
    else:
        bot.send_message(message.chat.id, "U must finish ur game")


@bot.message_handler(commands=['surrender'])
def surrender(message):
    states = sqlite3.connect('Tic_tac_toe.db')
    sql = states.cursor()
    check_reg(states, sql, message)
    player = sql.execute(f"SELECT Current_State FROM players_state WHERE Chat_id = {message.chat.id}").fetchone()
    del states
    chat_id = message.chat.id
    if player[0] == PlayerState.PLAY_WITH_BOT:
        set_player_state(chat_id, PlayerState.WAIT)
        games = sqlite3.connect('bot_games.db')
        games_sql = games.cursor()
        games_sql.execute(f"DELETE FROM bot_games WHERE Chat_id = {chat_id}")
        games.commit()
        send_message(bot, chat_id, "As u wish")
    if player[0] == PlayerState.PLAY_LOCAL:
        set_player_state(chat_id, PlayerState.WAIT)
        games = sqlite3.connect('local_games.db')
        games_sql = games.cursor()
        games_sql.execute(f"DELETE FROM local_games WHERE Chat_id = {chat_id}")
        games.commit()
        send_message(bot, chat_id, "As u wish")
    if player[0] == PlayerState.WAIT_FRIEND:
        set_player_state(chat_id, PlayerState.WAIT)
        games = sqlite3.connect('friend_requests.db')
        games_sql = games.cursor()
        games_sql.execute(f"DELETE FROM friend_requests WHERE Chat_id = {chat_id}")
        games.commit()
        send_message(bot, chat_id, "As u wish")
    if player[0] == PlayerState.PLAY_WITH_PLAYER:
        games = sqlite3.connect('multiplayer_games.db')
        games_sql = games.cursor()
        current_game = games_sql.execute(f"SELECT Chat_id_first, Chat_id_second FROM multiplayer_games WHERE Chat_id_first = {chat_id} OR Chat_id_second = {chat_id}").fetchone()
        set_player_state(current_game[0], PlayerState.WAIT)
        set_player_state(current_game[1], PlayerState.WAIT)
        games_sql.execute(f"DELETE FROM multiplayer_games WHERE Chat_id_first = {chat_id} OR Chat_id_second = {chat_id}")
        games.commit()
        opponent = current_game[0]
        if current_game[0] == chat_id:
            opponent = current_game[1]
        send_message(bot, opponent, "Your opponent left the game")

        send_message(bot, chat_id, "As u wish")
    if player[0] == PlayerState.WAIT_RANDOM:
        set_player_state(chat_id, PlayerState.WAIT)
        global searching_players
        searching_players = None
        send_message(bot, chat_id, "As u wish")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global is_adding
    while is_adding:
        pass
    if not(message.chat.id in current_users):

        is_adding = True
        current_users.append(message.chat.id)
        is_adding = False

        states_bd = sqlite3.connect('Tic_tac_toe.db')
        states_sql = states_bd.cursor()
        player = states_sql.execute(f"SELECT Current_State FROM players_state WHERE Chat_id = {message.chat.id}").fetchone()
        if player[0] == PlayerState.PLAY_WITH_BOT:
            versus_bot_logic(bot, message)
        elif player[0] == PlayerState.PLAY_LOCAL:
            local_logic(bot, message)
        elif player[0] == PlayerState.WAIT_FRIEND:
            invite_logic(bot, message)
        elif player[0] == PlayerState.PLAY_WITH_PLAYER:
            multiplayer_logic(bot, message)

        current_users.remove(message.chat.id)


bot.polling(none_stop=True)

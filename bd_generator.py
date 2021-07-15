import sqlite3

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
    Game_field TEXT,
    Bot_Symbol TEXT,
    Game_State INTEGER);
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

friend_requests = sqlite3.connect('friend_requests.db')
friend_sql = friend_requests.cursor()
friend_sql.execute("""CREATE TABLE IF NOT EXISTS friend_requests(
    Chat_id INTEGER,
    Friend_User_Name TEXT
);""")
friend_requests.commit()

del friend_requests

multiplayer_games = sqlite3.connect("multiplayer_games.db")
multiplayer_sql = multiplayer_games.cursor()
multiplayer_sql.execute("""CREATE TABLE IF NOT EXISTS multiplayer_games(
    Chat_id_first INTEGER,
    Chat_id_second INTEGER,
    Game_field TEXT,
    Game_State INTEGER
);""")

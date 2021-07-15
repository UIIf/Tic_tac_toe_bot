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

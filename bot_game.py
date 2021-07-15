from base_functions import *
import random


def bot_step(bot, current_game, games, games_sql):
    chat_id = current_game[0]
    field = current_game[1].split(" ")
    opponent_symbol = "1"
    symbol = current_game[2]
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
            send_message(bot, chat_id, text)
            set_player_state(chat_id, PlayerState.WAIT)
        else:
            txt_field = ' '.join(field)
            games_sql.execute(f"""UPDATE bot_games SET Game_field = "{txt_field}" WHERE Chat_id = {chat_id} """)
            msg = generate_field_and_keyboard(field)
            send_message(bot, chat_id, msg[0], msg[1])
    else:
        field[next_step] = symbol
        text = "You lose\n" + generate_field_and_keyboard(field)[0]
        games_sql.execute(f"DELETE FROM bot_games WHERE Chat_id = {chat_id}")
        send_message(bot, chat_id, text)
        set_player_state(chat_id, PlayerState.WAIT)

    games.commit()


def versus_bot_logic(bot, message):

    # Pull current game
    games = sqlite3.connect('bot_games.db')
    games_sql = games.cursor()
    current_game = games_sql.execute(f"SELECT * FROM bot_games WHERE Chat_id = {message.chat.id}").fetchone()
    # print(current_game[3], BotGameStates.CHOOSE_SIDE.value)
    if current_game[3] == BotGameStates.CHOOSE_SIDE.value:
        if message.text == "⭕️.":
            games_sql.execute(f"""UPDATE bot_games SET Bot_Symbol = "{1}" WHERE Chat_id = {message.chat.id}""")
            bot_step(bot, games_sql.execute(f"SELECT * FROM bot_games WHERE Chat_id = {message.chat.id}").fetchone(), games,
                     games_sql)
        elif message.text != "❌.":
            bot.send_message(bot, message.chat.id, "Pls use keyboard")
            return
        else:
            msg = generate_field_and_keyboard(["0", "0", "0", "0", "0", "0", "0", "0", "0"])
            send_message(bot, message.chat.id, msg[0], msg[1])
        games_sql.execute(f"UPDATE bot_games SET Game_State = {BotGameStates.WAIT_MOVE.value} WHERE Chat_id = {message.chat.id}")
        games.commit()
    else:
        try:
            temp = int(message.text)
            if (temp > 0) and (temp < 10):
                player_symbol = current_game[2]
                if player_symbol == "1":
                    player_symbol = "2"
                else:
                    player_symbol = "1"
                player_response_field = player_step(bot, current_game[0], current_game[1], player_symbol, temp)
                if win_chek(player_response_field) == "0":
                    if free_steps(player_response_field) == 0:
                        send_message(bot, message.chat.id, "Tie\n" + generate_field_and_keyboard(player_response_field)[0])
                        games_sql.execute(f"DELETE FROM bot_games WHERE Chat_id = {message.chat.id}")
                        set_player_state(message.chat.id, PlayerState.WAIT)
                    else:
                        games_sql.execute(f"""UPDATE bot_games SET Game_field = "{" ".join(player_response_field)}" WHERE Chat_id = {message.chat.id} """)
                        current_game = games_sql.execute(f"SELECT * FROM bot_games WHERE Chat_id = {message.chat.id}").fetchone()
                        bot_step(bot, current_game, games, games_sql)
                else:
                    send_message(bot, message.chat.id, "You win\n" + generate_field_and_keyboard(player_response_field)[0])
                    games_sql.execute(f"DELETE FROM bot_games WHERE Chat_id = {message.chat.id}")
                    set_player_state(message.chat.id, PlayerState.WAIT)
                games.commit()
        except ValueError:
            bot.send_message(bot, message.chat.id, "Smth go wrong")
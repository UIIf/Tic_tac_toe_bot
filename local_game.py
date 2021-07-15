from base_functions import *


def local_logic(bot, message):
    games = sqlite3.connect('local_games.db')
    games_sql = games.cursor()
    try:
        temp = int(message.text)
        current_game = games_sql.execute(f"SELECT * FROM local_games WHERE Chat_id = {message.chat.id}").fetchone()
        if (temp > 0) and (temp < 10):
            player_response_field = player_step(current_game[1], current_game[2], temp)
            if player_response_field is None:
                bot.send_message(message.chat.id, "Pleas use keyboard")
            else:
                win = win_chek(player_response_field)
                if(win != "0") or (free_steps(player_response_field) == 0):

                    if win != "0":
                        msg = "❌"
                        if current_game[2] == "2":
                            msg = "⭕️"
                        msg += " Win\n"
                    else:
                        msg = "Tie\n"

                    msg += generate_field_and_keyboard(player_response_field)[0]
                    send_message(bot, message.chat.id, msg)
                    games_sql.execute(f"DELETE FROM local_games WHERE Chat_id = {message.chat.id}")
                    set_player_state(message.chat.id, PlayerState.WAIT)
                else:
                    symbol = "1"
                    if current_game[2] == "1":
                        symbol = "2"
                    games_sql.execute(f"""UPDATE local_games SET Current_Symbol = {symbol}, Game_field = "{" ".join(player_response_field)}" WHERE Chat_id = {message.chat.id}""")
                    msg = generate_field_and_keyboard(player_response_field)
                    send_message(bot, message.chat.id, msg[0],msg[1])
                games.commit()
    except ValueError:
        bot.send_message(bot, message.chat.id, "Smth go wrong")
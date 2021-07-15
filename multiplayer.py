import sqlite3
from base_functions import MpGameStates, SendMessagesBoth, player_step, win_chek, send_massage_both, generate_field_and_keyboard, free_steps
from telebot import types


def multiplayer_logic(bot, message):
    mp_games = sqlite3.connect("multiplayer_games.db")
    mp_sql = mp_games.cursor()
    chat_id = message.chat.id
    current_game = mp_sql.execute(f"""SELECT * FROM multiplayer_games WHERE Chat_id_first = {chat_id} OR Chat_id_second = {chat_id} """).fetchone()
    if not(current_game is None):
        if(current_game[3] == MpGameStates.WAIT_MOVE_S) or (current_game[3] == MpGameStates.WAIT_MOVE_F):
            player_turn = False
            player_symbol = None
            second_id = current_game[0]
            if (current_game[0] == chat_id) and (current_game[3] == MpGameStates.WAIT_MOVE_F):
                player_turn = True
                player_symbol = "1"
                second_id = current_game[1]
            elif (current_game[1] == chat_id) and (current_game[3] == MpGameStates.WAIT_MOVE_S):
                player_turn = True
                player_symbol = "2"
            else:
                bot.send_message(chat_id, "Wait ur turn")

            if player_turn:
                temp = message.text
                try:
                    temp = int(temp)
                    if(temp > 0) and (temp < 10):
                        player_response_field = player_step(current_game[2], player_symbol, temp)
                        if player_response_field is None:
                            bot.send_message(chat_id, "Pleas use keyboard")
                        else:
                            win = win_chek(player_response_field)
                            msg = generate_field_and_keyboard(player_response_field)
                            if win != '0' or free_steps(player_response_field) < 1:
                                markup_in_game = types.ReplyKeyboardMarkup(one_time_keyboard=True)
                                markup_in_game.add("Rematch", "/surrender")
                                if win != '0':
                                    send_massage_both(bot, chat_id, second_id, "You win\n" + msg[0], SendMessagesBoth.FOR_BOTH, markup_in_game=markup_in_game, second_player_text="You Lose\n" + msg[0])
                                else:
                                    send_massage_both(bot, chat_id, second_id, "Tie\n" + msg[0],
                                                      SendMessagesBoth.FOR_BOTH, markup_in_game=markup_in_game)
                                mp_sql.execute(f"""UPDATE multiplayer_games SET Game_state = {MpGameStates.WAIT_REMATCH} WHERE Chat_id_first = {current_game[0]}""")
                            else:
                                gs = MpGameStates.WAIT_MOVE_F
                                if player_symbol == "1":
                                    gs = MpGameStates.WAIT_MOVE_S
                                mp_sql.execute(f"""UPDATE multiplayer_games SET Game_field = "{" ".join(player_response_field)}", Game_State = {gs} WHERE Chat_id_first = {current_game[0]} """)
                                send_massage_both(bot, second_id, chat_id, msg[0], SendMessagesBoth.FOR_FIRST, msg[1], "Your turn\n")

                    else:
                        bot.send_message(chat_id, "Pleas use keyboard")
                except ValueError:
                    bot.send_message(chat_id, "Pleas use keyboard")
        elif current_game[3] == MpGameStates.WAIT_REMATCH:
            if message.text.lower() == "rematch":
                second_id = current_game[0]
                if chat_id == second_id:
                    second_id = current_game[1]
                mp_sql.execute(f"""UPDATE multiplayer_games SET Game_State = {MpGameStates.ONE_READY}, Chat_id_first = {chat_id},Chat_id_second = {second_id}  WHERE Chat_id_first = {current_game[0]}  """)
                bot.send_message(second_id, "Your opponent want's rematch")

        elif current_game[3] == MpGameStates.ONE_READY:
            if message.text.lower() == "rematch" and chat_id == current_game[1]:
                mp_sql.execute(
                    f"""UPDATE multiplayer_games SET Game_State = {MpGameStates.WAIT_MOVE_F},Game_field = "0 0 0 0 0 0 0 0 0" WHERE Chat_id_first = {current_game[0]}  """)
                msg = generate_field_and_keyboard(["0", "0", "0", "0", "0", "0", "0", "0", "0"])
                send_massage_both(bot, current_game[0], current_game[1], msg[0], SendMessagesBoth.FOR_FIRST, msg[1], "Yor turn\n")
        mp_games.commit()

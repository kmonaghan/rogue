import os
import shelve

def save_game(player, game_map, message_log, game_state, pubsub):
    with shelve.open("savegame", "n") as data_file:
        data_file["player_index"] = game_map.current_level.entities.lst.index(player)
        data_file["game_map"] = game_map
        data_file["message_log"] = message_log
        data_file["game_state"] = game_state
        data_file["pubsub"] = pubsub

def load_game():
    if not os.path.isfile("savegame.db"):
        raise FileNotFoundError

    with shelve.open("savegame", "r") as data_file:
        player_index = data_file["player_index"]
        game_map = data_file["game_map"]
        message_log = data_file["message_log"]
        game_state = data_file["game_state"]
        pubsub = data_file["pubsub"]

    player = game_map.current_level.entities.lst[player_index]

    return player, game_map, message_log, game_state, pubsub

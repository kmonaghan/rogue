import tcod
import numpy as np

from utils.utils import matprint

def generate_dijkstra_player_map(game_map, player):
    walkable = game_map.current_level.make_walkable_array()

    dijk = tcod.dijkstra_new(walkable)
    tcod.dijkstra_compute(dijk, player.x, player.y)

    dijk_dist = np.zeros(game_map.current_level.walkable.shape, dtype=np.int8)
    for y in range(game_map.current_level.height):
        for x in range(game_map.current_level.width):
            dijk_dist[x, y] = tcod.dijkstra_get_distance(dijk, x, y)

    dijk_dist[np.where(dijk_dist == -1)] = 0

    game_map.current_level.dijkstra_player = dijk_dist

def generate_dijkstra_flee_map(game_map, player):
    #if not game_map.current_level.dijkstra_player:
    generate_dijkstra_player_map(game_map, player)

    dijk_dist = np.copy(game_map.current_level.dijkstra_player)
    #print(np.amax(dijk_dist))
    max_distance = np.where(dijk_dist == np.amax(dijk_dist))
    #print(max_distance)
    dijk_dist[np.where(dijk_dist != 0)] *= -1.2

    updated_dijk = tcod.dijkstra_new(dijk_dist)
    tcod.dijkstra_compute(updated_dijk, max_distance[0][0], max_distance[1][0])

    flee_dist = np.zeros((game_map.current_level.width, game_map.current_level.height), dtype=np.float32)
    for y in range(game_map.current_level.height):
        for x in range(game_map.current_level.width):
            flee_dist[x, y] = tcod.dijkstra_get_distance(updated_dijk, x, y)

    flee_dist[np.where(flee_dist == -1)] = 0

    game_map.current_level.dijkstra_flee = flee_dist

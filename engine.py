import tcod as libtcod

from fov_functions import initialize_fov, recompute_fov
from game_messages import Message
import game_states
from input_handlers import handle_keys, handle_mouse, handle_main_menu
from loader_functions.initialize_new_game import get_constants, get_game_variables
from loader_functions.data_loaders import load_game, save_game
from menus import main_menu, message_box
from render_functions import clear_all, render_all
from map_objects.point import Point
import quest
import pubsub

from etc.enum import (
    ResultTypes, InputTypes, GameStates,
    INVENTORY_STATES, INPUT_STATES, CANCEL_STATES)
'''TODO: Move
'''

from utils.utils import (
    flatten_list_of_dictionaries,
    unpack_single_key_dict,
    get_key_from_single_key_dict,
    get_all_entities_with_component_in_position)

def get_user_input(key, mouse):
    event = libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse, True)
    return key, mouse

def play_game(player, game_map, message_log, game_state, con, panel, constants):
    fov_recompute = True

    fov_map = initialize_fov(game_map)

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    targeting_item = None
    quest_request = None

    # Initial values for game states
    game_state = GameStates.PLAYER_TURN
    previous_game_state = game_state
    # Stacks for holding the results of player and enemy turns.
    player_turn_results = []
    enemy_turn_results = []

    # A counter for how many times we have incremented the game loop on this
    # floor.  Used to trigger updates that happen regularly with regards to
    # game loop.  For example, graphical shimmering of water and ice.
    game_loop = -1

    while not libtcod.console_is_window_closed():

        game_loop += 1

        #---------------------------------------------------------------------
        # Recompute the player's field of view if necessary.
        #---------------------------------------------------------------------
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y,
                            constants['fov_radius'], constants['fov_light_walls'],
                            constants['fov_algorithm'])

        #---------------------------------------------------------------------
        # Render and display the dungeon and its inhabitates.
        #---------------------------------------------------------------------
        render_all(con, panel, player, game_map, fov_map, fov_recompute, message_log,
                   constants['screen_width'], constants['screen_height'], constants['bar_width'],
                   constants['panel_height'], constants['panel_y'], mouse, constants['colors'], game_state, quest_request)

        fov_recompute = False

        clear_all(con, game_map)

        #---------------------------------------------------------------------
        # Render any menus.
        #---------------------------------------------------------------------

        #---------------------------------------------------------------------
        # Blit the subconsoles to the main console and flush all rendering.
        #---------------------------------------------------------------------

        libtcod.console_flush()

        #---------------------------------------------------------------------
        # Get key input from the player.
        #---------------------------------------------------------------------
        user_input, mouse_action = get_user_input(key, mouse)

        input_result = handle_keys(user_input, game_state)
        mouse_action = handle_mouse(mouse)

        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        player_turn_results = []

        action, action_value = unpack_single_key_dict(input_result)

        if action == InputTypes.GAME_RESTART:
            player, game_map, message_log, game_state = get_game_variables(constants)
            fov_map = initialize_fov(game_map)
            fov_recompute = True
            libtcod.console_clear(con)
            game_state = GameStates.ENEMY_TURN

        if action == InputTypes.DEBUG_ON:
            game_states.debug = True
            fov_recompute = True

        if action == InputTypes.DEBUG_OFF:
            game_states.debug = False
            fov_recompute = True

        if player.level.can_level_up():
            game_state = GameStates.LEVEL_UP

        if action == InputTypes.WAIT:
            game_state = GameStates.ENEMY_TURN

        '''
        Menu Options
        '''
        if action == InputTypes.CHARACTER_SCREEN:
            previous_game_state = game_state
            game_state = GameStates.CHARACTER_SCREEN

        if action == InputTypes.INVENTORY_DROP:
            previous_game_state = game_state
            game_state = GameStates.INVENTORY_DROP

        if action == InputTypes.INVENTORY_EQUIP:
            previous_game_state = game_state
            game_state = GameStates.INVENTORY_EQUIP

        if action == InputTypes.INVENTORY_EXAMINE:
            previous_game_state = game_state
            game_state = GameStates.INVENTORY_EXAMINE
        '''
        if action == InputTypes.INVENTORY_INDEX:
            previous_game_state = game_state
            game_state = GameStates.INVENTORY_INDEX
        '''
        if (action == InputTypes.INVENTORY_INDEX) and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(
                player.inventory.items):
            item = player.inventory.items[inventory_index]

            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities=game_map.entities, fov_map=fov_map, game_map=game_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))
            elif game_state == GameStates.EXAMINE_INVENTORY:
                player_turn_results.extend(player.inventory.examine_item(item))

        if action == InputTypes.INVENTORY_THROW:
            previous_game_state = game_state
            game_state = GameStates.INVENTORY_THROW

        if action == InputTypes.INVENTORY_USE:
            previous_game_state = game_state
            game_state = GameStates.INVENTORY_USE

        if action == InputTypes.LEVEL_UP:
            if level_up == 'hp':
                player.level.level_up_stats(0)
            elif level_up == 'str':
                player.level.level_up_stats(1)
            elif level_up == 'def':
                player.level.level_up_stats(2)

            game_state = previous_game_state

        if action == InputTypes.QUEST_LIST:
            previous_game_state = game_state
            game_state = GameStates.QUEST_LIST

        if action == InputTypes.QUEST_RESPONSE:
            quest_request.owner.start_quest(game_map)
            message_log.add_message(Message('Started quest: ' + quest_request.title, libtcod.yellow))
            quest_request = None
            game_state = previous_game_state

        if (action == InputTypes.QUEST_INDEX) and previous_game_state != GameStates.PLAYER_DEAD and quest_index < len(quest.active_quests):
            selected_quest = quest.active_quests[quest_index]
            message_log.add_message(selected_quest.status())
            game_state = previous_game_state

        if game_state == GameStates.PLAYER_TURN:
            if action == InputTypes.MOVE:
                dx, dy = action_value
                point = Point(player.x + dx, player.y + dy)

                if not game_map.is_blocked(point):
                    target = game_map.get_blocking_entities_at_location(point)

                    if target:
                        if target.questgiver:
                            quest_results = target.questgiver.talk(player)
                            player_turn_results.extend(quest_results)
                        elif target.defence:
                            attack_results = player.offence.attack(target)
                            player_turn_results.extend(attack_results)
                    else:
                        player.movement.move(dx, dy)
                        quest_results = quest.check_quest_for_location(player.point)
                        player_turn_results.extend(quest_results)

                        fov_recompute = True

                        game_map.update_entity_map()

                    game_state = GameStates.ENEMY_TURN
            elif action == InputTypes.PICKUP:
                for entity in game_map.entity_map[player.x][player.y]:
                    if entity.item:
                        pickup_results = player.inventory.add_item(entity)
                        player_turn_results.extend(pickup_results)

                        game_map.update_entity_map()
                else:
                    message_log.add_message(Message('There is nothing here to pick up.', libtcod.yellow))
            elif action == InputTypes.TAKE_STAIRS:
                if (game_map.check_for_stairs(player.x, player.y)):
                        game_map.next_floor(player, message_log, constants)
                        fov_map = initialize_fov(game_map)
                        fov_recompute = True
                        libtcod.console_clear(con)

                        break
                else:
                    message_log.add_message(Message('There are no stairs here.', libtcod.yellow))

        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = player.inventory.use(targeting_item, entities=game_map.entities, fov_map=fov_map,
                                                        target_x=target_x, target_y=target_y)
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})

        if action == InputTypes.EXIT:
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY, GameStates.EXAMINE_INVENTORY, GameStates.SHOW_QUESTS, GameStates.CHARACTER_SCREEN):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            elif game_state == GameStates.QUEST_ONBOARDING:
                player_turn_results.append({'quest_cancelled': True})
            else:
                save_game(player, game_map, message_log, game_state)

                return True

        if action == InputTypes.FULLSCREEN:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        #----------------------------------------------------------------------
        # Process the results stack
        #......................................................................
        # We are done processing player inputs, and may have some results on
        # the player turn stack.  Process the stack by popping off the top
        # result from the queue.  There are many different possible results,
        # so each is handled with a dedicated handler.
        #
        # Note: Handling a result may result in other results being added to
        # the stack, so we continually process the results stack until it is
        # empty.
        #----------------------------------------------------------------------

        while player_turn_results != []:

            # Sort the turn results stack by the priority order.
            player_turn_results = sorted(
                flatten_list_of_dictionaries(player_turn_results),
                key = lambda d: get_key_from_single_key_dict(d))

            result = player_turn_results.pop()
            result_type, result_data = unpack_single_key_dict(result)

            # Handle a simple message.
            if result_type == ResultTypes.MESSAGE:
                message = result_data
                message_log.add_message(message)
            # Handle death.
            if result_type == ResultTypes.DEAD_ENTITY:
                dead_entity = result_data
                print(">>>>>")
                print(result_data.describe())
                if dead_entity == player:
                    player_turn_results.extend(kill_player(player))
                    game_state = GameStates.PLAYER_DEAD
                else:
                    #player_turn_results.extend(dead_entity.death.npc_death(game_map))
                    dead_entity.death.npc_death(game_map)
                    entity_map_needs_update = True

            # Add an item to the inventory, and remove it from the game map.
            if result_type == ResultTypes.ADD_ITEM_TO_INVENTORY:
                #entity, item = result_data
                #entity.inventory.add(item)
                #item.commitable.delete(game_map)
                game_map.entities.remove(item_added)
                game_state = GameStates.ENEMY_TURN

            # Remove consumed items from inventory
            if result_type == ResultTypes.DISCARD_ITEM:
                #item, consumed = result_data
                #if consumed:
                #    player.inventory.remove(item)
                game_state = GameStates.ENEMY_TURN

            # Remove dropped items from inventory and place on the map
            if result_type == ResultTypes.DROP_ITEM_FROM_INVENTORY:
                #entity, item = result_data
                #entity.inventory.remove(item)
                #item.x, item.y = entity.x, entity.y
                #game_map.entities.append(item)
                game_map.add_entity_to_map(item_dropped)
                game_state = GameStates.ENEMY_TURN

            if result_type == ResultTypes.EQUIP:
                equip_results = player.equipment.toggle_equip(equip)

                for equip_result in equip_results:
                    equipped = equip_result.get('equipped')
                    dequipped = equip_result.get('dequipped')

                    if equipped:
                        message_log.add_message(Message('You equipped the {0}'.format(equipped.name)))

                    if dequipped:
                        message_log.add_message(Message('You dequipped the {0}'.format(dequipped.name)))

                game_state = GameStates.ENEMY_TURN
            if result_type == ResultTypes.QUEST_ONBOARDING:
                quest_request = result_data

                previous_game_state = GameStates.PLAYER_TURN
                game_state = GameStates.QUEST_ONBOARDING

            if result_type == GameStates.QUEST_RESPONSE:
                pass

            '''
            if targeting:
                previous_game_state = GameStates.PLAYER_TURN
                game_state = GameStates.TARGETING

                targeting_item = targeting

                message_log.add_message(targeting_item.item.targeting_message)

            if targeting_cancelled:
                game_state = previous_game_state

                message_log.add_message(Message('Targeting cancelled'))
            '''

        pubsub.pubsub.process_queue(fov_map, game_map)

        #game_state = GameStates.ENEMY_TURN

        #-------------------------------------------------------------------
        # All enemies and terrain take thier turns.
        #-------------------------------------------------------------------
        if game_state == GameStates.ENEMY_TURN:

            for entity in game_map.entities:
                if entity.health and entity.health.dead:
                    entity.death.decompose(game_map)
                elif entity.ai:
                    # Enemies move and attack if possible.
                    entity.energy.increase_energy()
                    if entity.energy.take_action():
                        enemy_turn_results.extend(entity.ai.take_turn(player, fov_map, game_map))

            game_state = GameStates.PLAYER_TURN

        #---------------------------------------------------------------------
        # Process all result actions of enemy turns.
        #---------------------------------------------------------------------
        entity_map_needs_update = False

        while enemy_turn_results != []:

            enemy_turn_results = sorted(
                flatten_list_of_dictionaries(enemy_turn_results),
                key = lambda d: get_key_from_single_key_dict(d))

            result = enemy_turn_results.pop()
            result_type, result_data = unpack_single_key_dict(result)

            # Handle a move towards action.  Move towards a target.
            if result_type == ResultTypes.MOVE_TOWARDS:
               monster, target_x, target_y = result_data
               monster.movable.move_towards(game_map, target_x, target_y)
               entity_map_needs_update = True
            # Handle a move random adjacent action.  Move to a random adjacent
            # square.
            if result_type == ResultTypes.MOVE_RANDOM_ADJACENT:
               monster = result_data
               monster.movable.move_to_random_adjacent(game_map)
               entity_map_needs_update = True
            # Handle a simple message.
            if result_type == ResultTypes.MESSAGE:
                message = result_data
                message_log.add_message(message)
            # Add a new entity to the game.
            if result_type == ResultTypes.ADD_ENTITY:
                entity = result_data
                entity.commitable.commit(game_map)
                entity_map_needs_update = True
            # Remove an entity from the game.
            if result_type == ResultTypes.REMOVE_ENTITY:
                entity = result_data
                entity.commitable.delete(game_map)
                entity_map_needs_update = True
            # Handle death.
            if result_type == ResultTypes.DEAD_ENTITY:
                dead_entity = result_data

                if dead_entity == player:
                    game_state = GameStates.PLAYER_DEAD

                dead_entity.death.npc_death(game_map)
                entity_map_needs_update = True

            if entity_map_needs_update:
                game_map.update_entity_map()
                entity_map_needs_update = False

        #---------------------------------------------------------------------
        # And done...
        #---------------------------------------------------------------------

        game_map.update_entity_map()

        pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.TICK))

        pubsub.pubsub.process_queue(fov_map, game_map)

def main():
    constants = get_constants()

    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

    libtcod.console_init_root(constants['screen_width'], constants['screen_height'], constants['window_title'], False)

    con = libtcod.console_new(constants['screen_width'], constants['screen_height'])
    panel = libtcod.console_new(constants['screen_width'], constants['panel_height'])

    player = None
    game_map = None
    message_log = None
    game_state = None

    show_main_menu = True
    show_load_error_message = False

    main_menu_background_image = libtcod.image_load('menu_background.png')

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if show_main_menu:
            main_menu(con, main_menu_background_image, constants['screen_width'],
                      constants['screen_height'])

            if show_load_error_message:
                message_box(con, 'No save game to load', 50, constants['screen_width'], constants['screen_height'])

            libtcod.console_flush()

            action = handle_keys(key, GameStates.GAME_START)

            if len(action) > 0:
                result_type, result_data = unpack_single_key_dict(action)
                if show_load_error_message and (result_type == InputTypes.GAME_LOAD):
                    show_load_error_message = False
                elif result_type == InputTypes.GAME_NEW:
                    player, game_map, message_log, game_state = get_game_variables(constants)

                    show_main_menu = False
                elif result_type == InputTypes.GAME_LOAD:
                    try:
                        player, game_map, message_log, game_state = load_game()
                        show_main_menu = False
                    except FileNotFoundError:
                        show_load_error_message = True
                elif result_type == InputTypes.GAME_EXIT:
                    break

        else:
            print("playing")
            libtcod.console_clear(con)
            play_game(player, game_map, message_log, game_state, con, panel, constants)

            show_main_menu = True


if __name__ == '__main__':
    main()

import tcod

from game_messages import Message
from input_handlers import handle_keys, handle_mouse, handle_main_menu
from loader_functions.initialize_new_game import get_constants, get_game_variables
from loader_functions.data_loaders import load_game, save_game
from menus import main_menu, message_box
from render_functions import get_names_under_mouse, render_info_console, render_message_console, render_menu_console
from map_objects.point import Point
import quest
import pubsub

from etc.configuration import CONFIG
from etc.enum import (
    ResultTypes, InputTypes, GameStates, LevelUp,
    INVENTORY_STATES, INPUT_STATES, CANCEL_STATES)

from utils.utils import (
    flatten_list_of_dictionaries,
    unpack_single_key_dict,
    get_key_from_single_key_dict,
    get_all_entities_with_component_in_position)

def get_user_input(key, mouse):
    event = tcod.sys_wait_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse, True)
    return key, mouse

def play_game(player, game_map, message_log, game_state, consoles, constants):
    root_console, map_console, info_console, message_console, menu_console = consoles

    for console in consoles:
        console.clear(fg=(255, 255, 63))

    fov_recompute = True

    key = tcod.Key()
    mouse = tcod.Mouse()

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

    while not tcod.console_is_window_closed():
        player_turn_results.clear()
        enemy_turn_results.clear()

        game_loop += 1

        #---------------------------------------------------------------------
        # Recompute the player's field of view.
        #---------------------------------------------------------------------
        game_map.current_level.compute_fov(player.x, player.y,
                                            algorithm=constants['fov_algorithm'],
                                            radius=constants['fov_radius'],
                                            light_walls=constants['fov_light_walls'])
        fov_recompute = False

        #---------------------------------------------------------------------
        # Render and display the dungeon and its inhabitates.
        #---------------------------------------------------------------------
        game_map.current_level.update_and_draw_all(map_console)

        #---------------------------------------------------------------------
        # Render infomation panels.
        #---------------------------------------------------------------------
        render_info_console(info_console, player, game_map)
        render_message_console(message_console, message_log)

        #---------------------------------------------------------------------
        # Blit the subconsoles to the main console and flush all rendering.
        #---------------------------------------------------------------------
        root_console.clear(fg=(255, 255, 63))

        if CONFIG.get('debug'):
            game_map.current_level.walkable_for_entity_under_mouse(mouse)

        map_console.blit(root_console, 0, 0, 0, 0,
                          map_console.width, map_console.height)

        root_console.print(1, constants['panel_y'] - 1, get_names_under_mouse(mouse, game_map), tcod.white)

        info_console.blit(root_console, 0, constants['panel_y'], 0, 0,
                          constants['info_panel_width'], constants['panel_height'])
        message_console.blit(root_console, constants['info_panel_width'], constants['panel_y'], 0, 0,
                          constants['message_panel_width'], constants['panel_height'])

        if game_state in INPUT_STATES:
            #---------------------------------------------------------------------
            # Render any menus.
            #---------------------------------------------------------------------
            menu_console = render_menu_console(game_state, CONFIG.get('full_screen_width'), CONFIG.get('full_screen_height'), player, quest_request)

            menu_console.blit(root_console,
                                (root_console.width - menu_console.width) // 2,
                                (root_console.height - menu_console.height) // 2,
                                0, 0,
                                CONFIG.get('full_screen_width'), CONFIG.get('full_screen_height'))

        tcod.console_flush()

        #---------------------------------------------------------------------
        # Get key input from the player.
        #---------------------------------------------------------------------
        user_input, mouse_action = get_user_input(key, mouse)

        input_result = handle_keys(user_input, game_state)
        mouse_action = handle_mouse(mouse)

        if (len(input_result) == 0):
            if CONFIG.get('debug'):
                #print("No corresponding result for key press.")
                pass
            continue

        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        player_turn_results = []

        action, action_value = unpack_single_key_dict(input_result)

        if action == InputTypes.GAME_EXIT:
            return GameStates.GAME_EXIT
            break

        if action == InputTypes.GAME_RESTART:
            player, game_map, message_log, game_state = get_game_variables(constants)
            game_map.create_floor(player, constants)
            fov_recompute = True
            game_state = GameStates.PLAYER_TURN
            previous_game_state = game_state

            continue

        if action == InputTypes.DEBUG_ON:
            CONFIG.update({'debug': True})
            fov_recompute = True

        if action == InputTypes.DEBUG_OFF:
            CONFIG.update({'debug': False})
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

        if action == InputTypes.INVENTORY_EXAMINE:
            previous_game_state = game_state
            game_state = GameStates.INVENTORY_EXAMINE

        if action == InputTypes.INVENTORY_THROW:
            previous_game_state = game_state
            game_state = GameStates.INVENTORY_THROW

        if action == InputTypes.INVENTORY_USE:
            previous_game_state = game_state
            game_state = GameStates.INVENTORY_USE

        if (action == InputTypes.INVENTORY_INDEX
            and previous_game_state != GameStates.GAME_OVER
            and action_value < len(player.inventory.items)):
            item = player.inventory.items[action_value]

            if game_state == GameStates.INVENTORY_USE:
                player_turn_results.extend(player.inventory.use(item, game_map=game_map))
            elif game_state == GameStates.INVENTORY_DROP:
                player_turn_results.extend(player.inventory.drop_item(item))
            elif game_state == GameStates.INVENTORY_EXAMINE:
                player_turn_results.extend(player.inventory.examine_item(item))

        if action == InputTypes.LEVEL_UP:
            player.level.level_up_stats(action_value)
            game_state = previous_game_state

        if action == InputTypes.QUEST_LIST:
            previous_game_state = game_state
            game_state = GameStates.QUEST_LIST

        if action == InputTypes.QUEST_RESPONSE:
            if action_value:
                quest_request.owner.start_quest(game_map)
                message_log.add_message(Message('Started quest: ' + quest_request.title, tcod.yellow))
            quest_request = None
            game_state = previous_game_state

        if (action == InputTypes.QUEST_INDEX
            and previous_game_state != GameStates.GAME_OVER
            and action_value < len(quest.active_quests)):
            selected_quest = quest.active_quests[action_value]
            message_log.add_message(selected_quest.status())
            game_state = previous_game_state

        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = player.inventory.use(targeting_item, entities=game_map.entities, game_map=game_map,
                                                        target_x=target_x, target_y=target_y)
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})

        if action == InputTypes.EXIT:
            if game_state in CANCEL_STATES:
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            elif game_state == GameStates.QUEST_ONBOARDING:
                player_turn_results.append({'quest_cancelled': True})
            else:
                game_state = GameStates.GAME_PAUSED
                continue

        if action == InputTypes.FULLSCREEN:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

        if game_state == GameStates.PLAYER_TURN:
            if player.health.dead:
                game_state = GameStates.GAME_OVER
            elif action == InputTypes.MOVE:
                dx, dy = action_value
                point = Point(player.x + dx, player.y + dy)

                if game_map.current_level.walkable[player.x + dx, player.y + dy]:
                    if game_map.current_level.blocked[player.x + dx, player.y + dy]:
                        target = game_map.current_level.entities.get_entities_in_position((player.x + dx, player.y + dy))

                        if target[0].questgiver:
                            quest_results = target[0].questgiver.talk(player)
                            player_turn_results.extend(quest_results)
                        elif target[0].defence:
                            attack_results = player.offence.attack(target[0])
                            player_turn_results.extend(attack_results)
                    else:
                        player.movement.move(dx, dy, game_map.current_level)
                        player_turn_results.extend(quest.check_quest_for_location(player))

                        fov_recompute = True

                    game_state = GameStates.ENEMY_TURN
            elif action == InputTypes.PICKUP:
                entities = game_map.current_level.entities.get_entities_in_position((player.x, player.y))
                for entity in entities:
                    if entity.item:
                        player_turn_results.extend([{
                            ResultTypes.ADD_ITEM_TO_INVENTORY: entity
                        }])
                else:
                    message = Message('There is nothing here to pick up.', tcod.yellow)
                    pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = message))

            elif action == InputTypes.TAKE_STAIRS:
                if (game_map.check_for_stairs(player.x, player.y)):
                        game_map.next_floor(player, constants)
                        fov_recompute = True
                        message = Message('You take a moment to rest and recover your strength.', tcod.light_violet)
                        pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = message))

                        continue
                else:
                    message = Message('There are no stairs here.', tcod.yellow)
                    pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = message))


        updated_game_state, quest_request = process_results_stack(game_map, player, player_turn_results, pubsub)

        if updated_game_state and updated_game_state != game_state:
            previous_game_state = game_state
            game_state = updated_game_state

        pubsub.pubsub.process_queue(game_map)

        #-------------------------------------------------------------------
        # All enemies and terrain take their turns.
        #-------------------------------------------------------------------
        if game_state == GameStates.ENEMY_TURN:

            for entity in game_map.current_level.entities:
                if entity.health and entity.health.dead:
                    entity.death.decompose(game_map)
                elif entity.ai:
                    # Enemies move and attack if possible.
                    entity.energy.increase_energy()
                    if entity.energy.take_action():
                        enemy_turn_results.extend(entity.ai.take_turn(player, game_map))

            game_state = GameStates.PLAYER_TURN

        updated_game_state, _ = process_results_stack(game_map, player, enemy_turn_results, pubsub)

        if updated_game_state and updated_game_state != game_state:
            previous_game_state = game_state
            game_state = updated_game_state

        #---------------------------------------------------------------------
        # And done...so broadcast a tick
        #---------------------------------------------------------------------
        pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.TICK))

        pubsub.pubsub.process_queue(game_map)

def process_results_stack(game_map, entity, turn_results, pubsub):
    update_game_state = None
    quest_request = None
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
    while turn_results != []:
        # Sort the turn results stack by the priority order.
        #print(turn_results)
        turn_results = sorted(
            flatten_list_of_dictionaries(turn_results),
            key = lambda d: get_key_from_single_key_dict(d))

        result = turn_results.pop()
        result_type, result_data = unpack_single_key_dict(result)

        # Handle a simple message.
        if result_type == ResultTypes.MESSAGE:
            message = result_data
            pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = message))

        # Handle death.
        if result_type == ResultTypes.DEAD_ENTITY:
            update_game_state = result_data.death.npc_death(game_map)

        # Add an item to the inventory, and remove it from the game map.
        if result_type == ResultTypes.ADD_ITEM_TO_INVENTORY:
            turn_results.extend(entity.inventory.add_item(result_data))

            update_game_state = GameStates.ENEMY_TURN

        # Remove consumed items from inventory
        if result_type == ResultTypes.DISCARD_ITEM:
            #item, consumed = result_data
            #if consumed:
            entity.inventory.remove(result_data)
            game_map.current_level.remove_entity(result_data)
            update_game_state = GameStates.ENEMY_TURN

        # Remove dropped items from inventory and place on the map
        if result_type == ResultTypes.DROP_ITEM_FROM_INVENTORY:
            game_map.current_level.add_entity(result_data)
            message = Message('{0} dropped the {1}'.format(entity.name, result_data.name), tcod.yellow)
            pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = message))

            update_game_state = GameStates.ENEMY_TURN

        if result_type == ResultTypes.EQUIP:
            equip_results = entity.equipment.toggle_equip(result_data)

            for equip_result in equip_results:
                equipped = equip_result.get('equipped')
                dequipped = equip_result.get('dequipped')

                if equipped:
                    message = Message('{0} equipped the {1}'.format(entity.name, equipped.name))

                if dequipped:
                    message = Message('{0} dequipped the {1}'.format(entity.name, dequipped.name))

                pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = message))

            update_game_state = GameStates.ENEMY_TURN
        if result_type == ResultTypes.QUEST_ONBOARDING:
            quest_request = result_data
            update_game_state = GameStates.QUEST_ONBOARDING

        if result_type == GameStates.QUEST_RESPONSE:
            pass

        # Handle a move towards action.  Move towards a target.
        if result_type == ResultTypes.MOVE_TOWARDS:
           npc, target_x, target_y = result_data
           #print("ResultTypes.MOVE_TOWARDS: " + npc.name)
           npc.movement.move_astar(Point(target_x, target_y), game_map)
        # Handle a move random adjacent action.  Move to a random adjacent
        # square.
        if result_type == ResultTypes.MOVE_RANDOM_ADJACENT:
           npc = result_data
           npc.movement.move_to_random_adjacent(game_map)

        # Add a new entity to the game.
        if result_type == ResultTypes.ADD_ENTITY:
            result_data.commitable.commit(game_map)
        # Remove an entity from the game.
        if result_type == ResultTypes.REMOVE_ENTITY:
            game_map.current_level.remove_entity(result_data)
            #entity.commitable.delete(game_map)

        '''
        if targeting:
            update_game_state = GameStates.TARGETING

            targeting_item = targeting

            message_log.add_message(targeting_item.item.targeting_message)

        if targeting_cancelled:
            game_state = previous_game_state

            message_log.add_message(Message('Targeting cancelled'))
        '''

    return update_game_state, quest_request

def main():
    constants = get_constants()

    tcod.console_set_custom_font(
        "arial10x10.png",
        tcod.FONT_LAYOUT_TCOD | tcod.FONT_TYPE_GREYSCALE,
    )

    root_console = tcod.console_init_root(CONFIG.get('full_screen_width'), CONFIG.get('full_screen_height'), constants['window_title'], False, order='F')
    map_console = tcod.console.Console(constants['map_width'], constants['map_height'], 'F')
    info_panel =  tcod.console.Console(constants['info_panel_width'], constants['panel_height'], 'F')
    message_panel = tcod.console.Console(constants['message_panel_width'], constants['panel_height'], 'F')
    menu_console = tcod.console.Console(constants['map_width'], constants['map_height'], 'F')

    consoles = [root_console, map_console, info_panel, message_panel, menu_console]

    player = None
    game_map = None
    message_log = None
    game_state = None

    show_main_menu = True
    show_load_error_message = False

    main_menu_background_image = tcod.image_load('menu_background.png')

    key = tcod.Key()
    mouse = tcod.Mouse()

    while not tcod.console_is_window_closed():
        if game_state == GameStates.GAME_EXIT:
            break

        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)

        if show_main_menu:
            main_menu(root_console, main_menu_background_image, CONFIG.get('full_screen_width'),
                      CONFIG.get('full_screen_height'))

            if show_load_error_message:
                message_box(map_console, 'No save game to load', 50, CONFIG.get('full_screen_width'), constants['screen_height'])

            tcod.console_flush()

            action = handle_keys(key, GameStates.GAME_START)

            if len(action) > 0:
                result_type, result_data = unpack_single_key_dict(action)
                if show_load_error_message and (result_type == InputTypes.GAME_LOAD):
                    show_load_error_message = False
                elif result_type == InputTypes.GAME_NEW:
                    player, game_map, message_log, game_state = get_game_variables(constants)
                    game_map.create_floor(player, constants)

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
            message_log.add_message(Message('Let\'s get ready to rock and/or roll!.', tcod.yellow))

            game_state = play_game(player, game_map, message_log, game_state, consoles, constants)

            show_main_menu = True


if __name__ == '__main__':
    main()

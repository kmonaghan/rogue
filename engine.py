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

def play_game(player, game_map, message_log, game_state, con, panel, constants):
    fov_recompute = True

    fov_map = initialize_fov(game_map)

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    game_state = game_states.GameStates.PLAYERS_TURN
    previous_game_state = game_state

    targeting_item = None
    quest_request = None

    while not libtcod.console_is_window_closed():
        #libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, constants['fov_radius'], constants['fov_light_walls'],
                          constants['fov_algorithm'])

        render_all(con, panel, player, game_map, fov_map, fov_recompute, message_log,
                   constants['screen_width'], constants['screen_height'], constants['bar_width'],
                   constants['panel_height'], constants['panel_y'], mouse, constants['colors'], game_state, quest_request)

        fov_recompute = False

        #libtcod.console_flush()

        clear_all(con, game_map)

        game_map.update_entity_map()

        libtcod.console_flush()
        libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse, True)

        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse)

        turn_on_debug = action.get('debug_on')
        turn_off_debug = action.get('debug_off')
        move = action.get('move')
        wait = action.get('wait')
        pickup = action.get('pickup')
        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')
        examine_inventory = action.get('examine_inventory')
        inventory_index = action.get('inventory_index')
        take_stairs = action.get('take_stairs')
        level_up = action.get('level_up')
        show_character_screen = action.get('show_character_screen')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')
        quest_list = action.get('quest_list')
        quest_response = action.get('quest_response')
        quest_index = action.get('quest_index')
        restart_game = action.get('restart_game')

        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        player_turn_results = []

        if (restart_game):
            player, game_map, message_log, game_state = get_game_variables(constants)
            fov_map = initialize_fov(game_map)
            fov_recompute = True
            libtcod.console_clear(con)
            game_state = game_states.GameStates.ENEMY_TURN

        if player.level.can_level_up():
            game_state = game_states.GameStates.LEVEL_UP

        if level_up:
            if level_up == 'hp':
                player.level.level_up_stats(0)
            elif level_up == 'str':
                player.level.level_up_stats(1)
            elif level_up == 'def':
                player.level.level_up_stats(2)

            game_state = previous_game_state

        if turn_on_debug:
            game_states.debug = turn_on_debug
            fov_recompute = True

        if turn_off_debug:
            game_states.debug = False
            fov_recompute = True

        '''
        Menu Options
        '''
        if show_character_screen:
            previous_game_state = game_state
            game_state = game_states.GameStates.CHARACTER_SCREEN

        if show_inventory:
            previous_game_state = game_state
            game_state = game_states.GameStates.SHOW_INVENTORY

        if drop_inventory:
            previous_game_state = game_state
            game_state = game_states.GameStates.DROP_INVENTORY

        if examine_inventory:
            previous_game_state = game_state
            game_state = game_states.GameStates.EXAMINE_INVENTORY

        if quest_list:
            previous_game_state = game_state
            game_state = game_states.GameStates.SHOW_QUESTS

        if quest_response:
            quest_request.owner.start_quest(game_map)
            message_log.add_message(Message('Started quest: ' + quest_request.title, libtcod.yellow))
            quest_request = None
            game_state = previous_game_state

        if quest_index is not None and previous_game_state != game_states.GameStates.PLAYER_DEAD and quest_index < len(quest.active_quests):
            selected_quest = quest.active_quests[quest_index]
            message_log.add_message(selected_quest.status())
            game_state = previous_game_state

        if inventory_index is not None and previous_game_state != game_states.GameStates.PLAYER_DEAD and inventory_index < len(
                player.inventory.items):
            item = player.inventory.items[inventory_index]

            if game_state == game_states.GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities=game_map.entities, fov_map=fov_map, game_map=game_map))
            elif game_state == game_states.GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))
            elif game_state == game_states.GameStates.EXAMINE_INVENTORY:
                player_turn_results.extend(player.inventory.examine_item(item))


        if game_state == game_states.GameStates.PLAYERS_TURN:
            if move:
                dx, dy = move
                destination_x = player.x + dx
                destination_y = player.y + dy

                point = Point(destination_x, destination_y)
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
                        player.move(dx, dy)
                        quest_results = quest.check_quest_for_location(player.point)
                        player_turn_results.extend(quest_results)

                        fov_recompute = True

                    game_state = game_states.GameStates.ENEMY_TURN
            elif pickup:
                for entity in game_map.entity_map[player.x][player.y]:
                    if entity.item:
                        pickup_results = player.inventory.add_item(entity)
                        player_turn_results.extend(pickup_results)

                        break
                else:
                    message_log.add_message(Message('There is nothing here to pick up.', libtcod.yellow))
            elif take_stairs:
                if (game_map.check_for_stairs(player.x, player.y)):
                        game_map.next_floor(player, message_log, constants)
                        fov_map = initialize_fov(game_map)
                        fov_recompute = True
                        libtcod.console_clear(con)

                    #    break
                else:
                    message_log.add_message(Message('There are no stairs here.', libtcod.yellow))
            elif wait:
                game_state = game_states.GameStates.ENEMY_TURN

        if game_state == game_states.GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = player.inventory.use(targeting_item, entities=game_map.entities, fov_map=fov_map,
                                                        target_x=target_x, target_y=target_y)
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})

        if exit:
            if game_state in (game_states.GameStates.SHOW_INVENTORY, game_states.GameStates.DROP_INVENTORY, game_states.GameStates.EXAMINE_INVENTORY, game_states.GameStates.SHOW_QUESTS, game_states.GameStates.CHARACTER_SCREEN):
                game_state = previous_game_state
            elif game_state == game_states.GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            elif game_state == game_states.GameStates.QUEST_ONBOARDING:
                player_turn_results.append({'quest_cancelled': True})
            else:
                save_game(player, game_map, message_log, game_state)

                return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            killed_entity = player_turn_result.get('entity_dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            equip = player_turn_result.get('equip')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')
            quest_onboarding = player_turn_result.get('quest_onboarding')
            quest_cancelled = player_turn_result.get('quest_cancelled')
            fov_recompute = player_turn_result.get('fov_recompute')

            if message:
                message_log.add_message(message)

            if dead_entity:
                game_state = dead_entity.death.npc_death(game_map)

            if item_added:
                game_map.entities.remove(item_added)

                game_state = game_states.GameStates.ENEMY_TURN

            if item_consumed:
                game_state = game_states.GameStates.ENEMY_TURN

            if item_dropped:
                game_map.add_entity_to_map(item_dropped)

                game_state = game_states.GameStates.ENEMY_TURN

            if equip:
                equip_results = player.equipment.toggle_equip(equip)

                for equip_result in equip_results:
                    equipped = equip_result.get('equipped')
                    dequipped = equip_result.get('dequipped')

                    if equipped:
                        message_log.add_message(Message('You equipped the {0}'.format(equipped.name)))

                    if dequipped:
                        message_log.add_message(Message('You dequipped the {0}'.format(dequipped.name)))

                game_state = game_states.GameStates.ENEMY_TURN

            if targeting:
                previous_game_state = game_states.GameStates.PLAYERS_TURN
                game_state = game_states.GameStates.TARGETING

                targeting_item = targeting

                message_log.add_message(targeting_item.item.targeting_message)

            if targeting_cancelled:
                game_state = previous_game_state

                message_log.add_message(Message('Targeting cancelled'))

            if quest_onboarding:
                previous_game_state = game_states.GameStates.PLAYERS_TURN
                game_state = game_states.GameStates.QUEST_ONBOARDING

                quest_request = quest_onboarding

            if quest_cancelled:
                game_state = previous_game_state

        pubsub.pubsub.process_queue(fov_map, game_map)

        if game_state == game_states.GameStates.ENEMY_TURN:
            for entity in game_map.entities:
                if entity.health and entity.health.dead:
                    entity.death.decompose(game_map)
                elif entity.ai:
                    entity.energy.increase_energy()
                    if entity.energy.take_action():
                        #print(entity.name + "(" + entity.uuid + ") CAN take a turn")
                        enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map)

                        for enemy_turn_result in enemy_turn_results:
                            message = enemy_turn_result.get('message')
                            dead_entity = enemy_turn_result.get('dead')
                            killed_entity = enemy_turn_result.get('entity_dead')

                            if message:
                                message_log.add_message(message)

                            if killed_entity:
                                game_state = killed_entity.death.npc_death(game_map)
                                entity.onKill(killed_entity, game_map)

                            if dead_entity:
                                game_state = dead_entity.death.npc_death(game_map)

                                if (game_state == game_states.GameStates.PLAYER_DEAD) or (game_state == game_states.GameStates.GAME_COMPLETE):
                                    break

                        if (game_state == game_states.GameStates.PLAYER_DEAD) or (game_state == game_states.GameStates.GAME_COMPLETE):
                            break
                    else:
                        #print(entity.name + "(" + entity.uuid + ") can not take a turn yet")
                        pass

                game_map.update_entity_map()
            else:
                game_state = game_states.GameStates.PLAYERS_TURN

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

            action = handle_main_menu(key)

            new_game = action.get('new_game')
            load_saved_game = action.get('load_game')
            exit_game = action.get('exit')

            if show_load_error_message and (new_game or load_saved_game or exit_game):
                show_load_error_message = False
            elif new_game:
                player, game_map, message_log, game_state = get_game_variables(constants)

                show_main_menu = False
            elif load_saved_game:
                try:
                    player, game_map, message_log, game_state = load_game()
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error_message = True
            elif exit_game:
                break

        else:
            libtcod.console_clear(con)
            play_game(player, game_map, message_log, game_state, con, panel, constants)

            show_main_menu = True


if __name__ == '__main__':
    main()

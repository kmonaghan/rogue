import tcod
import tcod.event

from bestiary import create_player

from etc.colors import COLORS
from etc.configuration import CONFIG
from etc.enum import (
    ResultTypes, InputTypes, GameStates, LevelUp,
    INVENTORY_STATES, INPUT_STATES, CANCEL_STATES)

from game_messages import MessageLog

from input_handlers import handle_keys, handle_main_menu

from map_objects.game_map import GameMap
from map_objects.point import Point

from game_messages import Message

import pubsub

import quest

from render_functions import get_names_under_mouse, render_info_console, render_message_console, render_menu_console

from utils.utils import (
    flatten_list_of_dictionaries,
    unpack_single_key_dict,
    get_key_from_single_key_dict)

class MainMenu(tcod.event.EventDispatch):
    def __init__(self):
        pass

    def on_enter(self):
        tcod.sys_set_fps(60)

    def on_draw(self):
        pass

    def ev_keydown(self, event: tcod.event.KeyDown):
        print(event.sym)
        '''
            key_char = chr(key.c)

            if key_char == 'a':
                return {InputTypes.GAME_NEW: True}
            elif key_char == 'b':
                return {InputTypes.GAME_LOAD: True}
            elif key_char == 'c' or key.vk == libtcod.KEY_ESCAPE:
                return {InputTypes.GAME_EXIT: True}

            return {}
        '''

    def ev_quit(self, event: tcod.event.Quit):
        raise SystemExit()

class Rogue(tcod.event.EventDispatch):
    def __init__(self):
        self.recompute = True
        self.game_map = None
        self.fov_recompute = True
        self.map_console = tcod.console.Console(CONFIG.get('map_width'), CONFIG.get('map_height'), 'F')
        self.info_console = tcod.console.Console(CONFIG.get('info_panel_width'), CONFIG.get('panel_height'), 'F')
        self.message_console = tcod.console.Console(CONFIG.get('message_panel_width'), CONFIG.get('panel_height'), 'F')
        self.menu_console = tcod.console.Console(CONFIG.get('map_width'), CONFIG.get('map_height'), 'F')
        self.game_state = GameStates.PLAYER_TURN
        self.previous_game_state = None
        self.message_log = None
        self.motion = tcod.event.MouseMotion()
        self.lbut = self.mbut = self.rbut = 0
        self.quest_request = None

    def start_game(self):
        pubsub.pubsub = pubsub.PubSub()

        self.message_log = MessageLog(CONFIG.get('message_width'), CONFIG.get('message_height'))
        pubsub.pubsub.subscribe(pubsub.Subscription(self.message_log, pubsub.PubSubTypes.MESSAGE, pubsub.add_to_messages))

        self.player = create_player()

        self.game_map = GameMap()
        self.game_map.create_floor(self.player)

        self.game_state = GameStates.PLAYER_TURN
        self.fov_recompute = True

        quest.active_quests = []

        self.game_state = GameStates.PLAYER_TURN
        self.previous_game_state = None

        self.message_log.add_message(Message('Let\'s get ready to rock and/or roll!.', tcod.yellow))

    def on_enter(self):
        tcod.sys_set_fps(60)

    def on_draw(self):
        #---------------------------------------------------------------------
        # Recompute the player's field of view.
        #---------------------------------------------------------------------
        if self.fov_recompute:
            self.game_map.current_level.compute_fov(self.player.x, self.player.y,
                                                algorithm=CONFIG.get('fov_algorithm'),
                                                radius=CONFIG.get('fov_radius'),
                                                light_walls=CONFIG.get('fov_light_walls'))
            self.fov_recompute = False

        #---------------------------------------------------------------------
        # Render and display the dungeon and its inhabitates.
        #---------------------------------------------------------------------
        self.game_map.current_level.update_and_draw_all(self.map_console, self.player)

        #---------------------------------------------------------------------
        # Render infomation panels.
        #---------------------------------------------------------------------
        render_info_console(self.info_console, self.player, self.game_map)
        render_message_console(self.message_console, self.message_log)

        #---------------------------------------------------------------------
        # Blit the subconsoles to the main console and flush all rendering.
        #---------------------------------------------------------------------
        root_console.clear(fg=COLORS.get('console_background'))

        if CONFIG.get('debug'):
            self.game_map.current_level.walkable_for_entity_under_mouse(self.motion.tile.x, self.motion.tile.y)

        self.map_console.blit(root_console, 0, 0, 0, 0,
                          self.map_console.width, self.map_console.height)

        root_console.print(1, CONFIG.get('panel_y') - 1, get_names_under_mouse(self.motion.tile.x, self.motion.tile.y, self.game_map), tcod.white)

        self.info_console.blit(root_console, 0, CONFIG.get('panel_y'), 0, 0,
                          CONFIG.get('info_panel_width'), CONFIG.get('panel_height'))
        self.message_console.blit(root_console, CONFIG.get('info_panel_width'), CONFIG.get('panel_y'), 0, 0,
                          CONFIG.get('message_panel_width'), CONFIG.get('panel_height'))

        if self.game_state in INPUT_STATES:
            #---------------------------------------------------------------------
            # Render any menus.
            #---------------------------------------------------------------------
            self.menu_console = render_menu_console(self.game_state, CONFIG.get('full_screen_width'), CONFIG.get('full_screen_height'), self.player, self.quest_request)

            self.menu_console.blit(root_console,
                                (root_console.width - self.menu_console.width) // 2,
                                (root_console.height - self.menu_console.height) // 2,
                                0, 0,
                                CONFIG.get('full_screen_width'), CONFIG.get('full_screen_height'))

    def ev_keydown(self, event: tcod.event.KeyDown):
        print(event)

        #---------------------------------------------------------------------
        # Get key input from the self.player.
        #---------------------------------------------------------------------
        input_result = handle_keys(event, self.game_state)

        if (len(input_result) == 0):
            if CONFIG.get('debug'):
                #print("No corresponding result for key press.")
                pass
            return

        action, action_value = unpack_single_key_dict(input_result)
        self.process_turn(action, action_value)

    def ev_mousemotion(self, event: tcod.event.MouseMotion):
        self.motion = event

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown):
        if event.button == tcod.event.BUTTON_LEFT:
            self.lbut = True
        elif event.button == tcod.event.BUTTON_MIDDLE:
            self.mbut = True
        elif event.button == tcod.event.BUTTON_RIGHT:
            self.rbut = True

    def ev_mousebuttonup(self, event: tcod.event.MouseButtonUp):
        if event.button == tcod.event.BUTTON_LEFT:
            self.lbut = False
        elif event.button == tcod.event.BUTTON_MIDDLE:
            self.mbut = False
        elif event.button == tcod.event.BUTTON_RIGHT:
            self.rbut = False

    def ev_quit(self, event: tcod.event.Quit):
        raise SystemExit()

    def process_turn(self, action, action_value):
        player_turn_results = []

        if action == InputTypes.GAME_EXIT:
            self.game_state = GameStates.GAME_EXIT
            return

        if action == InputTypes.GAME_SAVE:
            save_game(self.player, self.game_map, message_log, self.game_state, pubsub.pubsub)
            return

        if action == InputTypes.GAME_RESTART:
            self.start_game()
            return

        if action == InputTypes.RELOAD_LEVEL:
            self.game_map.next_floor(self.player)
            return

        if action == InputTypes.DEBUG_ON:
            CONFIG.update({'debug': True})
            self.fov_recompute = True

        if action == InputTypes.DEBUG_OFF:
            CONFIG.update({'debug': False})
            self.fov_recompute = True

        if self.player.level.can_level_up():
            self.game_state = GameStates.LEVEL_UP

        if action == InputTypes.WAIT:
            self.game_state = GameStates.ENEMY_TURN

        '''
        Menu Options
        '''
        if action == InputTypes.CHARACTER_SCREEN:
            self.previous_game_state = self.game_state
            self.game_state = GameStates.CHARACTER_SCREEN

        if action == InputTypes.INVENTORY_DROP:
            self.previous_game_state = self.game_state
            self.game_state = GameStates.INVENTORY_DROP

        if action == InputTypes.INVENTORY_EXAMINE:
            self.previous_game_state = self.game_state
            self.game_state = GameStates.INVENTORY_EXAMINE

        if action == InputTypes.INVENTORY_THROW:
            self.previous_game_state = self.game_state
            self.game_state = GameStates.INVENTORY_THROW

        if action == InputTypes.INVENTORY_USE:
            self.previous_game_state = self.game_state
            self.game_state = GameStates.INVENTORY_USE

        if (action == InputTypes.INVENTORY_INDEX
            and self.previous_game_state != GameStates.GAME_OVER
            and action_value < len(self.player.inventory.items)):
            item = self.player.inventory.items[action_value]

            if self.game_state == GameStates.INVENTORY_USE:
                player_turn_results.extend(self.player.inventory.use(item, game_map=self.game_map))
            elif self.game_state == GameStates.INVENTORY_DROP:
                player_turn_results.extend(self.player.inventory.drop_item(item))
            elif self.game_state == GameStates.INVENTORY_EXAMINE:
                player_turn_results.extend(self.player.inventory.examine_item(item))

        if action == InputTypes.LEVEL_UP:
            self.player.level.level_up_stats(action_value)
            self.game_state = self.previous_game_state

        if action == InputTypes.QUEST_LIST:
            self.previous_game_state = self.game_state
            self.game_state = GameStates.QUEST_LIST

        if action == InputTypes.QUEST_RESPONSE:
            if action_value:
                self.quest_request.owner.start_quest(self.game_map)
                self.message_log.add_message(Message(f"Started quest: {self.quest_request.title}", tcod.yellow))
            self.quest_request = None
            self.game_state = self.previous_game_state

        if (action == InputTypes.QUEST_INDEX
            and self.previous_game_state != GameStates.GAME_OVER
            and action_value < len(quest.active_quests)):
            selected_quest = quest.active_quests[action_value]
            self.message_log.add_message(selected_quest.status())
            self.game_state = self.previous_game_state

        if self.game_state == GameStates.TARGETING:
            '''
            if left_click:
                target_x, target_y = left_click

                item_use_results = self.player.inventory.use(targeting_item, entities=game_map.entities, game_map=self.game_map,
                                                        target_x=target_x, target_y=target_y)
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})
            '''
            pass

        if action == InputTypes.EXIT:
            if self.game_state in CANCEL_STATES:
                self.game_state = self.previous_game_state
            elif self.game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            elif self.game_state == GameStates.QUEST_ONBOARDING:
                player_turn_results.append({'quest_cancelled': True})
            else:
                self.game_state = GameStates.GAME_PAUSED
                return

        if action == InputTypes.FULLSCREEN:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

        if self.game_state == GameStates.PLAYER_TURN:
            if self.player.health.dead:
                self.game_state = GameStates.GAME_OVER
            elif action == InputTypes.MOVE:
                dx, dy = action_value
                point = Point(self.player.x + dx, self.player.y + dy)

                if self.game_map.current_level.walkable[self.player.x + dx, self.player.y + dy]:
                    if self.game_map.current_level.blocked[self.player.x + dx, self.player.y + dy]:
                        targets = self.game_map.current_level.entities.get_entities_in_position((self.player.x + dx, self.player.y + dy))

                        targets_in_render_order = sorted(targets, key=lambda x: x.render_order.value)
                        print(targets_in_render_order)
                        target = targets[-1]
                        if target.questgiver:
                            quest_results = target.questgiver.talk(self.player)
                            player_turn_results.extend(quest_results)
                        elif not target.health.dead:
                            attack_results = self.player.offence.attack(target)
                            player_turn_results.extend(attack_results)
                    else:
                        self.player.movement.move(dx, dy, self.game_map.current_level)
                        player_turn_results.extend(quest.check_quest_for_location(self.player))

                        self.fov_recompute = True

                    self.game_state = GameStates.ENEMY_TURN
            elif action == InputTypes.PICKUP:
                entities = self.game_map.current_level.entities.get_entities_in_position((self.player.x, self.player.y))
                for entity in entities:
                    if entity.item:
                        player_turn_results.extend([{
                            ResultTypes.ADD_ITEM_TO_INVENTORY: entity
                        }])
                else:
                    message = Message('There is nothing here to pick up.', tcod.yellow)
                    pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = message))

            elif action == InputTypes.TAKE_STAIRS:
                if (game_map.check_for_stairs(self.player.x, self.player.y)):
                        self.game_map.next_floor(self.player, constants)
                        self.fov_recompute = True
                        message = Message('You take a moment to rest and recover your strength.', tcod.light_violet)
                        pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = message))

                        #continue
                        return
                else:
                    message = Message('There are no stairs here.', tcod.yellow)
                    pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = message))


        self.process_results_stack(self.player, player_turn_results)

        pubsub.pubsub.process_queue(self.game_map)

        #-------------------------------------------------------------------
        # All enemies and terrain take their turns.
        #-------------------------------------------------------------------
        enemy_turn_results = []

        if self.game_state == GameStates.ENEMY_TURN:
            self.game_map.current_level.clear_paths()
            for entity in self.game_map.current_level.entities:
                if entity.health and entity.health.dead:
                    entity.death.decompose(self.game_map)
                elif entity.ai:
                    # Enemies move and attack if possible.
                    entity.energy.increase_energy()
                    if entity.energy.take_action():
                        print("Taking turn for " + str(entity))
                        enemy_turn_results.extend(entity.ai.take_turn(self.game_map))

            self.game_state = GameStates.PLAYER_TURN

        self.process_results_stack(self.player, enemy_turn_results)

        #---------------------------------------------------------------------
        # And done...so broadcast a tick
        #---------------------------------------------------------------------
        pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.TICK))

        pubsub.pubsub.process_queue(self.game_map)

    def process_results_stack(self, entity, turn_results):
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
                self.game_state = result_data.death.npc_death(self.game_map)

            # Add an item to the inventory, and remove it from the game map.
            if result_type == ResultTypes.ADD_ITEM_TO_INVENTORY:
                turn_results.extend(entity.inventory.add_item(result_data))

                self.game_state = GameStates.ENEMY_TURN

            # Remove consumed items from inventory
            if result_type == ResultTypes.DISCARD_ITEM:
                #item, consumed = result_data
                #if consumed:
                entity.inventory.remove(result_data)
                self.game_map.current_level.remove_entity(result_data)
                self.game_state = GameStates.ENEMY_TURN

            # Remove dropped items from inventory and place on the map
            if result_type == ResultTypes.DROP_ITEM_FROM_INVENTORY:
                self.game_map.current_level.add_entity(result_data)
                message = Message(f"{entity.name} dropped the {result_data.name}", tcod.yellow)
                pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = message))

                self.game_state = GameStates.ENEMY_TURN

            if result_type == ResultTypes.EQUIP:
                equip_results = entity.equipment.toggle_equip(result_data)

                for equip_result in equip_results:
                    equipped = equip_result.get('equipped')
                    dequipped = equip_result.get('dequipped')

                    if equipped:
                        message = Message(f"{entity.name} equipped the {equipped.name}")

                    if dequipped:
                        message = Message(f"{entity.name} dequipped the {dequipped.name}")

                    pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = message))

                self.game_state = GameStates.ENEMY_TURN
            if result_type == ResultTypes.QUEST_ONBOARDING:
                self.quest_request = result_data
                self.previous_game_state = self.game_state
                self.game_state = GameStates.QUEST_ONBOARDING

            if result_type == GameStates.QUEST_RESPONSE:
                pass

            # Handle a move towards action.  Move towards a target.
            if result_type == ResultTypes.MOVE_TOWARDS:
               npc, target_x, target_y = result_data
               npc.movement.attempt_move(Point(target_x, target_y), self.game_map)
            # Handle a move towards action.  Move towards a target following a particular path.
            if result_type == ResultTypes.MOVE_WITH_PATH:
               npc, path = result_data
               self.game_map.current_level.paths.append(path)
               npc.movement.attempt_move(Point(path[0][0], path[0][1]), self.game_map)
            # Handle a move random adjacent action.  Move to a random adjacent
            # square.
            if result_type == ResultTypes.MOVE_RANDOM_ADJACENT:
               npc = result_data
               npc.movement.move_to_random_adjacent(self.game_map)

            # Add a new entity to the game.
            if result_type == ResultTypes.ADD_ENTITY:
                self.game_map.current_level.add_entity(result_data)
            # Remove an entity from the game.
            if result_type == ResultTypes.REMOVE_ENTITY:
                self.game_map.current_level.remove_entity(result_data)

            '''
            if targeting:
                self.game_state = GameStates.TARGETING

                targeting_item = targeting

                self.message_log.add_message(targeting_item.item.targeting_message)

            if targeting_cancelled:
                self.game_state = self.previous_game_state

                self.message_log.add_message(Message('Targeting cancelled'))
            '''

current_game = Rogue()
main_menu = MainMenu()

def main():
    global current_game, root_console

    tcod.console_set_custom_font(
        "arial10x10.png",
        tcod.FONT_LAYOUT_TCOD | tcod.FONT_TYPE_GREYSCALE,
    )

    root_console = tcod.console_init_root(CONFIG.get('full_screen_width'),
                                            CONFIG.get('full_screen_height'),
                                            CONFIG.get('window_title'), False, order='F')

    current_game.start_game()

    while not tcod.console_is_window_closed():
        root_console.clear(fg=COLORS.get('console_background'))

        if current_game.game_state == GameStates.GAME_EXIT:
            raise SystemExit()

        '''
                if show_main_menu:
                    root_console.clear(fg=(255, 255, 255))

                    main_menu(root_console, main_menu_background_image, CONFIG.get('full_screen_width'),
                              CONFIG.get('full_screen_height'))

                    if show_load_error_message:
                        message_box(map_console, 'No saved game to load', 50, CONFIG.get('full_screen_width'), constants['screen_height'])

                    tcod.console_flush()

                    action = handle_keys(key, GameStates.GAME_START)

                    if len(action) > 0:
                        result_type, result_data = unpack_single_key_dict(action)
                        if show_load_error_message and (result_type == InputTypes.GAME_LOAD):
                            show_load_error_message = False
                        elif result_type == InputTypes.GAME_NEW:
                            player, game_map, message_log, game_state = get_game_variables(constants)
                            game_map.create_floor(player)

                            show_main_menu = False
                        elif result_type == InputTypes.GAME_LOAD:
                            try:
                                player, game_map, message_log, game_state, pubsub.pubsub = load_game()
                                show_main_menu = False
                            except FileNotFoundError:
                                show_load_error_message = True
                        elif result_type == InputTypes.GAME_EXIT:
                            break
        '''
        #if self.game_state == GameStates.GAME_START:
        #    main_menu.on_draw()
        #else:
        current_game.on_draw()

        tcod.console_flush()
        handle_events()

def handle_events():
    for event in tcod.event.get():
        #if self.game_state == GameStates.GAME_START:
        #    main_menu.dispatch(event)
        #else:
        current_game.dispatch(event)

if __name__ == "__main__":
    main()

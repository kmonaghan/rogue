import datetime
import logging

import tcod
import tcod.event
from time import sleep

import equipment

from bestiary import create_player

from utils.dijkstra_maps import generate_dijkstra_player_map, generate_dijkstra_flee_map

from components.sleep import Sleep

from etc.colors import COLORS
from etc.configuration import CONFIG
from etc.enum import (
    ResultTypes, InputTypes, GameStates, LevelUp, MessageType, StairOption,
    INVENTORY_STATES, INPUT_STATES, MENU_STATES, CANCEL_STATES, Interactions)
from equipment import identified_items, potion_descriptions

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
    get_key_from_single_key_dict,
    resource_path)

class MainMenu(tcod.event.EventDispatch):
    def __init__(self):
        pass

    def on_enter(self):
        tcod.sys_set_fps(60)

    def on_draw(self):
        pass

    def ev_keydown(self, event: tcod.event.KeyDown):
        logging.info(event.sym)
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
        self.info_console = tcod.console.Console(CONFIG.get('map_width'), CONFIG.get('info_panel_height'), 'F')
        self.message_console = tcod.console.Console(CONFIG.get('map_width'), CONFIG.get('message_panel_height'), 'F')
        self.menu_console = tcod.console.Console(CONFIG.get('map_width'), CONFIG.get('map_height'), 'F')
        self.game_state = GameStates.PLAYER_TURN
        self.previous_game_state = None
        self.message_log = None
        self.motion = tcod.event.MouseMotion()
        self.lbut = self.mbut = self.rbut = 0
        self.quest_request = None
        self.using_item = None

    def start_fresh_game(self):
        logging.basicConfig(filename=f'{resource_path("log")}/{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.log', filemode='w', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=CONFIG.get('logging_level'))

        pubsub.pubsub = pubsub.PubSub()

        self.message_log = MessageLog(CONFIG.get('message_width'), CONFIG.get('message_height'))
        pubsub.pubsub.subscribe(pubsub.Subscription(self.message_log, pubsub.PubSubTypes.MESSAGE, pubsub.add_to_messages))

        self.player = create_player()

        self.game_map = GameMap()
        self.game_map.create_floor(self.player)

        self.start_game()

    def start_game(self):
        self.fov_recompute = True

        quest.active_quests = []
        identified_items = {}
        potion_descriptions = {}

        self.game_state = GameStates.PLAYER_TURN
        self.previous_game_state = None

        self.message_log.add_message(Message('Let\'s get ready to rock and/or roll!', tcod.yellow))

    def on_enter(self):
        tcod.sys_set_fps(60)

    def on_draw(self):
        #---------------------------------------------------------------------
        # Recompute the player's field of view.
        #---------------------------------------------------------------------
        if self.fov_recompute:
            self.game_map.current_level.compute_fov(self.player.x, self.player.y,
                                                algorithm=self.player.fov.fov_algorithm,
                                                radius=self.player.fov.fov_radius,
                                                light_walls=self.player.fov.fov_light_walls)
            generate_dijkstra_player_map(self.game_map, self.player)

            if self.player.sleep:
                self.game_map.current_level.npc_fov = tcod.map.compute_fov(self.game_map.current_level.transparent, pov=(self.player.x, self.player.y),
                                                                    algorithm=tcod.FOV_RESTRICTIVE,
                                                                    light_walls=True,
                                                                    radius=10)

            else:
                self.game_map.current_level.npc_fov = self.game_map.current_level.fov

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

        under_mouse_text = get_names_under_mouse(self.motion.tile.x, self.motion.tile.y, self.game_map.current_level)
        text_height = root_console.get_height_rect(1, 0, root_console.width - 2, 10, under_mouse_text)

        root_console.print_box(
            1,
            CONFIG.get('info_panel_y') - text_height - 1,
            root_console.width - 2,
            text_height,
            under_mouse_text,
            fg=tcod.white,
            bg=None,
            alignment=tcod.LEFT,
        )

        self.info_console.blit(root_console, 0, CONFIG.get('info_panel_y'), 0, 0,
                          CONFIG.get('full_screen_width'), CONFIG.get('info_panel_height'))
        self.message_console.blit(root_console, 0, CONFIG.get('message_panel_y'), 0, 0,
                          CONFIG.get('full_screen_width'), CONFIG.get('message_panel_height'))

        if self.game_state in MENU_STATES:
            #---------------------------------------------------------------------
            # Render any menus.
            #---------------------------------------------------------------------
            exclude = []
            if self.using_item:
                exclude.append(self.using_item)

            self.menu_console = render_menu_console(self.game_state, self.player, self.quest_request, exclude)

            self.menu_console.blit(root_console, 0, 0, 0, 0,
                                CONFIG.get('full_screen_width'), CONFIG.get('full_screen_height'))

    def ev_keydown(self, event: tcod.event.KeyDown):
        #---------------------------------------------------------------------
        # Get key input from the self.player.
        #---------------------------------------------------------------------
        input_result = handle_keys(event, self.game_state)

        if (len(input_result) == 0):
            if CONFIG.get('debug'):
                #logging.info("No corresponding result for key press.")
                pass
            return

        action, action_value = unpack_single_key_dict(input_result)
        self.process_turn(action, action_value)

    def ev_mousemotion(self, event: tcod.event.MouseMotion):
        self.motion = event

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown):
        input_type = None
        if event.button == tcod.event.BUTTON_LEFT:
            self.lbut = True
            input_type = InputTypes.TARGETING
        elif event.button == tcod.event.BUTTON_MIDDLE:
            self.mbut = True
        elif event.button == tcod.event.BUTTON_RIGHT:
            self.rbut = True
            input_type = InputTypes.EXIT

        self.process_turn(input_type, (event.tile.x, event.tile.y))

    def ev_mousebuttonup(self, event: tcod.event.MouseButtonUp):
        if event.button == tcod.event.BUTTON_LEFT:
            self.lbut = False
        elif event.button == tcod.event.BUTTON_MIDDLE:
            self.mbut = False
        elif event.button == tcod.event.BUTTON_RIGHT:
            self.rbut = False

    def ev_quit(self, event: tcod.event.Quit):
        raise SystemExit()

    def game_actions(self, action, action_value):
        if action == InputTypes.GAME_EXIT:
            self.game_state = GameStates.GAME_EXIT
            return True

        if action == InputTypes.GAME_SAVE:
            save_game(self.player, self.game_map, message_log, self.game_state, pubsub.pubsub)
            return True

        if action == InputTypes.GAME_RESTART:
            self.start_fresh_game()
            return True

        if action == InputTypes.GAME_RESET:
            self.game_map.first_floor(self.player)
            self.start_game()
            return True

        if action == InputTypes.RELOAD_LEVEL:
            self.game_map.next_floor(self.player)
            self.fov_recompute = True
            return True

        return False

    def change_state_action(self, action, action_value):
        if action == InputTypes.CHARACTER_SCREEN:
            self.previous_game_state = self.game_state
            self.game_state = GameStates.CHARACTER_SCREEN
            return True

        if action == InputTypes.INVENTORY_DROP:
            self.previous_game_state = self.game_state
            self.game_state = GameStates.INVENTORY_DROP
            return True

        if action == InputTypes.INVENTORY_EXAMINE:
            self.previous_game_state = self.game_state
            self.game_state = GameStates.INVENTORY_EXAMINE
            return True

        if action == InputTypes.INVENTORY_THROW:
            self.previous_game_state = self.game_state
            self.game_state = GameStates.INVENTORY_THROW
            return True

        if action == InputTypes.INVENTORY_USE:
            self.previous_game_state = self.game_state
            self.game_state = GameStates.INVENTORY_USE
            return True

        if action == InputTypes.LEVEL_UP:
            self.player.level.level_up_stats(action_value)
            self.game_state = self.previous_game_state

        #This needs to come after leveling up or we get stuck in a loop
        if self.player.level.can_level_up():
            self.previous_game_state = self.game_state
            self.game_state = GameStates.LEVEL_UP
            return True

        if action == InputTypes.QUEST_LIST:
            self.previous_game_state = self.game_state
            self.game_state = GameStates.QUEST_LIST
            return True

        return False

    def debug_actions(self, action, action_value):
        if action == InputTypes.DEBUG_ON:
            CONFIG.update({'debug': True})
            self.fov_recompute = True

        if action == InputTypes.DEBUG_OFF:
            CONFIG.update({'debug': False})
            self.fov_recompute = True

        if action == InputTypes.SHOW_DIJKSTRA_PLAYER:
            CONFIG.update({'show_dijkstra_player': not CONFIG.get('show_dijkstra_player')})
            self.fov_recompute = True

        if action == InputTypes.SHOW_DIJKSTRA_FLEE:
            CONFIG.update({'show_dijkstra_flee': not CONFIG.get('show_dijkstra_flee')})
            self.fov_recompute = True

    def menu_actions(self, action, action_value):
        pass

    def quest_actions(self, action, action_value):
        if action == InputTypes.QUEST_RESPONSE:
            if action_value:
                self.quest_request.owner.start_quest(self.game_map)
                self.message_log.add_message(Message(f"Started quest: {self.quest_request.title}", tcod.yellow))
            self.quest_request = None
            self.game_state = self.previous_game_state

        if (action == InputTypes.QUEST_INDEX
            and self.previous_game_state != GameStates.GAME_OVER
            and action_value < len(quest.active_quests)):
            self.message_log.add_message(quest.active_quests[action_value].status())
            self.game_state = self.previous_game_state

    def player_actions(self, action, action_value):
        self.player.energy.take_action()

        player_turn_results = []

        player_on_turn_results = self.player.on_turn(self.game_map)
        self.process_results_stack(self.player, player_on_turn_results)

        if action == InputTypes.SLEEP:
            if not self.player.sleep:
                self.player.add_component(Sleep(), 'sleep')
                self.player.sleep.start()
                self.fov_recompute = True
                pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = Message('You have gone asleep.', COLORS.get('effect_text'))))

        if self.player.health.dead:
            self.game_state = GameStates.GAME_OVER
        elif self.player.sleep:
            finished = self.player.sleep.on_turn(self.game_map)
            if finished:
                pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = Message('You have woken up.', COLORS.get('effect_text'))))
                self.fov_recompute = True

            self.game_state = GameStates.ENEMY_TURN
        elif action == InputTypes.WAIT:
            self.game_state = GameStates.ENEMY_TURN
        elif action == InputTypes.MOVE:
            dx, dy = action_value
            point = Point(self.player.x + dx, self.player.y + dy)

            if self.game_map.current_level.accessible_tile(self.player.x + dx, self.player.y + dy):
                if self.game_map.current_level.blocked[self.player.x + dx, self.player.y + dy]:
                    targets = self.game_map.current_level.entities.get_entities_in_position((self.player.x + dx, self.player.y + dy))

                    targets_in_render_order = sorted(targets, key=lambda x: x.render_order.value, reverse=True)
                    target = targets_in_render_order[0]

                    if target.interaction.interaction_type == Interactions.QUESTGIVER:
                        quest_results = target.questgiver.talk(self.player)
                        player_turn_results.extend(quest_results)
                    elif target.interaction.interaction_type == Interactions.DOOR:
                        if target.locked:
                            can_unlock = False

                            if target.locked.requires_key:
                                all_keys = self.player.inventory.search(name = 'key')
                                for key_to_check in all_keys:
                                    if key_to_check.unlock.unlocks == target.uuid:
                                        can_unlock = True
                                        player_turn_results.extend([{ResultTypes.DISCARD_ITEM: key_to_check}])
                                        break
                            else:
                                can_unlock = True

                            if can_unlock:
                                target.locked.toggle()
                                self.game_map.current_level.update_entity_position(target)
                                self.fov_recompute = True

                                message = Message(f"You have unlocked the {target.name}.", tcod.yellow)
                                player_turn_results.extend([{ResultTypes.MESSAGE: message}])
                            else:
                                message = Message(f"The {target.name} is locked.", tcod.yellow)
                                player_turn_results.extend([{ResultTypes.MESSAGE: message}])
                    elif target.interaction.interaction_type == Interactions.FOE:
                        if target.health and not target.health.dead:
                            attack_results = self.player.offence.attack(target, self.game_map)
                            player_turn_results.extend(attack_results)
                else:
                    self.player.movement.move(dx, dy, self.game_map.current_level)
                    player_turn_results.extend(quest.check_quest_for_location(self.player))

                    self.fov_recompute = True

                self.game_state = GameStates.ENEMY_TURN
        elif action == InputTypes.PICKUP:
            entities = self.game_map.current_level.entities.get_entities_in_position((self.player.x, self.player.y))
            pickup = False
            for entity in entities:
                if entity.item:
                    if entity.identifiable and identified_items.get(entity.base_name):
                        entity.identifiable.identified = True
                    player_turn_results.extend([{
                        ResultTypes.ADD_ITEM_TO_INVENTORY: entity
                    }])
                    pickup = True
            if not pickup:
                message = Message('There is nothing here to pick up.', tcod.yellow)
                player_turn_results.extend([{ResultTypes.MESSAGE: message}])
        elif action == InputTypes.DOWN_LEVEL:
            self.game_map.next_floor(self.player)
            self.fov_recompute = True
            message = Message('You take a moment to rest and recover your strength.', tcod.light_violet)
            player_turn_results.extend([{ResultTypes.MESSAGE: message}])

            #continue
            return
        elif action == InputTypes.TAKE_STAIRS:
            stair_state = self.game_map.check_for_stairs(self.player.x, self.player.y)
            if stair_state == StairOption.GODOWN:
                self.game_map.next_floor(self.player)
                self.fov_recompute = True
                message = Message('You take a moment to rest and recover your strength.', tcod.light_violet)
                player_turn_results.extend([{ResultTypes.MESSAGE: message}])

                #continue
                return
            elif stair_state == StairOption.GOUP:
                self.game_map.previous_floor(self.player)
                self.fov_recompute = True

                return
            elif stair_state == StairOption.EXIT:
                self.game_state = GameStates.GAME_PAUSED
            else:
                message = Message('There are no stairs here.', tcod.yellow)
                player_turn_results.extend([{ResultTypes.MESSAGE: message}])

        self.process_results_stack(self.player, player_turn_results)

        pubsub.pubsub.process_queue(self.game_map)

    def npc_actions(self):
        self.game_map.current_level.clear_paths()
        for entity in self.game_map.current_level.entities:
            if entity == self.player:
                continue
            entity.energy.increase_energy()
            if entity.energy.take_action():
                if entity.level and entity.level.can_level_up():
                    entity.level.random_level_up(1)
                enemy_turn_results = entity.on_turn(self.game_map)
                self.process_results_stack(entity, enemy_turn_results)
                enemy_turn_results.clear()

                if entity.health and entity.health.dead:
                    entity.death.decompose(self.game_map)
                elif entity.ai:
                    # Enemies move and attack if possible.
                    enemy_turn_results.extend(entity.ai.take_turn(self.game_map))

                    self.process_results_stack(entity, enemy_turn_results)
                    enemy_turn_results.clear()

                pubsub.pubsub.process_queue(self.game_map)

    def process_turn(self, action, action_value):
        player_turn_results = []

        if self.game_actions(action, action_value):
            return

        if self.change_state_action(action, action_value):
            return

        self.debug_actions(action, action_value)

        self.quest_actions(action, action_value)

        if action == InputTypes.EXIT:
            if self.game_state in CANCEL_STATES:
                self.game_state = self.previous_game_state
                self.using_item = None
                if self.game_state == GameStates.QUEST_ONBOARDING:
                    player_turn_results.append({ResultTypes.QUEST_CANCELLED: True})
            else:
                self.previous_game_state = self.game_state
                self.game_state = GameStates.GAME_PAUSED
                return

        if (action == InputTypes.TARGETING
            and self.game_state == GameStates.TARGETING):
            target_x, target_y = action_value

            player_turn_results.extend(self.using_item.usable.use(game_map=self.game_map,
                                                            user=self.player,
                                                            target_x=target_x,
                                                            target_y=target_y))

        if (action == InputTypes.INVENTORY_INDEX
            and self.previous_game_state != GameStates.GAME_OVER
            and action_value < len(self.player.inventory.items)):

            items = self.player.inventory.items.copy()

            if self.using_item:
                items.remove(self.using_item)

            item = items[action_value]

            if self.game_state == GameStates.INVENTORY_USE:
                if item.usable:
                    self.using_item = item
                    player_turn_results.extend(item.usable.use(self.game_map, self.player))
                else:
                    player_turn_results.extend([{ResultTypes.EQUIP: item}])

            elif self.game_state == GameStates.INVENTORY_SELECT:
                player_turn_results.extend(self.using_item.usable.use(self.game_map, self.player, item))
                self.using_item = None
            elif self.game_state == GameStates.INVENTORY_DROP:
                player_turn_results.extend(self.player.inventory.drop_item(item))
            elif self.game_state == GameStates.INVENTORY_EXAMINE:
                player_turn_results.extend(self.player.inventory.examine_item(item))

        self.process_results_stack(self.player, player_turn_results)

        pubsub.pubsub.process_queue(self.game_map)

        #-------------------------------------------------------------------
        # Player takes their turn.
        #-------------------------------------------------------------------
        if (self.game_state == GameStates.PLAYER_TURN
            or self.game_state == GameStates.PLAYER_SLEEP):
            self.player_actions(action, action_value)

        if (self.game_state in INPUT_STATES
            or self.game_state == GameStates.GAME_OVER):
            return

        #-------------------------------------------------------------------
        # NPCs take their turns.
        #-------------------------------------------------------------------
        self.npc_actions()

        self.player.energy.increase_energy()
        if self.player.energy.can_act:
            if self.player.sleep:
                self.game_state = GameStates.PLAYER_SLEEP
            else:
                if not self.game_state in INPUT_STATES:
                    self.game_state = GameStates.PLAYER_TURN
        else:
            if not self.game_state in INPUT_STATES:
                self.game_state = GameStates.ENEMY_TURN

        if not self.game_state == GameStates.PLAYER_TURN:
            sleep(CONFIG.get('time_between_enemy_turns'))

        #---------------------------------------------------------------------
        # And done...so broadcast a tick
        #---------------------------------------------------------------------
        pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.TICK))

        pubsub.pubsub.process_queue(self.game_map)

    def process_results_stack(self, entity, turn_results):
        #----------------------------------------------------------------------
        # Process the results stack
        #......................................................................
        # We are done processing inputs, and may have some results on
        # the entity turn stack. Process the stack by popping off the top
        # result from the queue. There are many different possible results,
        # so each is handled with a dedicated handler.
        #
        # Note: Handling a result may result in other results being added to
        # the stack, so we continually process the results stack until it is
        # empty.
        #----------------------------------------------------------------------
        while turn_results != []:
            # Sort the turn results stack by the priority order.
            turn_results = sorted(
                flatten_list_of_dictionaries(turn_results),
                key = lambda d: get_key_from_single_key_dict(d))

            result = turn_results.pop()
            result_type, result_data = unpack_single_key_dict(result)

            # Handle a simple message.
            if result_type == ResultTypes.MESSAGE:
                message = result_data
                pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = message))

            if result_type == ResultTypes.FOV_RECOMPUTE:
                self.fov_recompute = True

            if result_type == ResultTypes.END_TURN:
                self.game_state = GameStates.ENEMY_TURN

            if result_type == ResultTypes.EARN_XP:
                if result_data['xp'] > 0:
                    result_data['earner'].level.add_xp(result_data['xp'])
                    message = Message(f"{result_data['earner'].name} gained {result_data['xp']} xp", COLORS.get('success_text'), target=result_data['earner'], type=MessageType.EVENT)
                    turn_results.extend([{ResultTypes.MESSAGE: message}])

            # Handle death.
            if result_type == ResultTypes.DEAD_ENTITY:
                self.game_state = result_data['dead'].death.npc_death(self.game_map)
                if entity == result_data['dead']:
                    turn_results = []
                if result_data['attacker'] and result_data['attacker'].ai:
                    result_data['attacker'].ai.remove_target(target=result_data['dead'])
                result_data['dead'].deregister_turn_all()

            if result_type == ResultTypes.TARGET_ITEM_IN_INVENTORY:
                self.game_state = GameStates.INVENTORY_SELECT

            if result_type == ResultTypes.CANCEL_TARGET_ITEM_IN_INVENTORY:
                self.using_item = None
                self.game_state = GameStates.PLAYER_TURN

            # Add an item to the inventory, and remove it from the game map.
            if result_type == ResultTypes.ADD_ITEM_TO_INVENTORY:
                turn_results.extend(entity.inventory.add_item(result_data))
                self.game_state = GameStates.ENEMY_TURN
            # Remove consumed items from inventory
            if result_type == ResultTypes.DISCARD_ITEM:
                entity.inventory.remove_item(result_data)
                self.game_state = GameStates.ENEMY_TURN
                self.using_item = None

            # Remove dropped items from inventory and place on the map
            if result_type == ResultTypes.DROP_ITEM_FROM_INVENTORY:
                self.game_map.current_level.add_entity(result_data)
                message = Message(f"{entity.name} dropped the {result_data.name}", COLORS.get('success_text'), target=entity, type=MessageType.EVENT)
                turn_results.extend([{ResultTypes.MESSAGE: message}])
                self.game_state = GameStates.ENEMY_TURN

            if result_type == ResultTypes.EQUIP:
                equip_results = entity.equipment.toggle_equip(result_data)

                for equip_result in equip_results:
                    equipped = equip_result.get('equipped')
                    dequipped = equip_result.get('dequipped')

                    if equipped:
                        message = Message(f"{entity.name} equipped the {equipped.name}", target=entity, type=MessageType.EVENT)

                    if dequipped:
                        message = Message(f"{entity.name} dequipped the {dequipped.name}", target=entity, type=MessageType.EVENT)

                    turn_results.extend([{ResultTypes.MESSAGE: message}])

                self.game_state = GameStates.ENEMY_TURN
            if result_type == ResultTypes.QUEST_ONBOARDING:
                self.quest_request = result_data
                self.previous_game_state = self.game_state
                self.game_state = GameStates.QUEST_ONBOARDING

            if result_type == ResultTypes.QUEST_CANCELLED:
                pass

            if result_type == ResultTypes.SET_POSITION:
                npc, point = result_data
                npc.movement.place(point.x, point.y, self.game_map.current_level)
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

            if result_type == ResultTypes.MOVE_FORCE:
               target, dx, dy, damage = result_data
               if damage > 0 and not target.movement.move(dx, dy, self.game_map.current_level):
                   damage_results, total_damage = target.health.take_damage(damage)
                   msg_text = '{0} crashes into the wall and takes {1} hit points damage.'
                   message = Message(msg_text.format(target.name, str(total_damage)), COLORS.get('damage_text'))
                   turn_results.extend([{ResultTypes.MESSAGE: message}])
                   turn_results.extend(damage_results)

            # Add a new entity to the game.
            if result_type == ResultTypes.ADD_ENTITY:
                self.game_map.current_level.add_entity(result_data)
            # Remove an entity from the game.
            if result_type == ResultTypes.REMOVE_ENTITY:
                self.game_map.current_level.remove_entity(result_data)
            if result_type == ResultTypes.TARGETING:
                self.previous_game_state = self.game_state
                self.game_state = GameStates.TARGETING

            if result_type == ResultTypes.COMMON_IDENT:
                identified_items[result_data] = True

current_game = Rogue()
main_menu = MainMenu()

def main():
    global current_game, root_console

    equipment.import_armour()
    equipment.import_weapons()

    tcod.console_set_custom_font(
        resource_path(CONFIG.get('font')),
        CONFIG.get('font_type') | tcod.FONT_TYPE_GREYSCALE,
    )

    root_console = tcod.console_init_root(CONFIG.get('full_screen_width'),
                                            CONFIG.get('full_screen_height'),
                                            CONFIG.get('window_title'), False,
                                            order='F', vsync=False)

    current_game.start_fresh_game()

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

        #Uncomment the following line to take a screenshot each turn
        #tcod.sys_save_screenshot()

        if (current_game.game_state == GameStates.ENEMY_TURN
            or current_game.game_state == GameStates.PLAYER_SLEEP):
            current_game.process_turn(None, None)
        else:
            handle_events()

def handle_events():
    for event in tcod.event.get():
        #if self.game_state == GameStates.GAME_START:
        #    main_menu.dispatch(event)
        #else:
        current_game.dispatch(event)

if __name__ == "__main__":
    main()

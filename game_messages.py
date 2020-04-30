import tcod

import textwrap

from etc.enum import DamageType, HealthStates, MessageType

class Message:
    def __init__(self, text, color=tcod.white, source=None, target=None, type=MessageType.SYSTEM):
        self.text = text
        self.color = color
        self.source = source
        self.target = target
        self.type = type

class MessageLog:
    def __init__(self, width, height):
        self.messages = []
        self.width = width
        self.height = height

    def add_message(self, message, game_map = None):
        if not message.type == MessageType.SYSTEM:
            if game_map and message.target:
                if not game_map.current_level.fov[message.target.x, message.target.y]:
                    return

        # Split the message if necessary, among multiple lines
        new_msg_lines = textwrap.wrap(message.text, self.width)

        for line in new_msg_lines:
            # If the buffer is full, remove the first line to make room for the new one
            if len(self.messages) == self.height:
                del self.messages[0]

            # Add the new line as a Message object, with the text and the color
            self.messages.append(Message(line, message.color))

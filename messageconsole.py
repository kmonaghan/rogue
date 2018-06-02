import libtcodpy as libtcod
import textwrap

#MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_WIDTH = 80 - 20 - 2
#MSG_HEIGHT = PANEL_HEIGHT - 1
MSG_HEIGHT = 7 - 1

#create the list of game messages and their colors, starts empty
game_msgs = []

def message(new_msg, color = libtcod.white):
    #split the message if necessary, among multiple lines
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        #if the buffer is full, remove the first line to make room for the new one
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]

        #add the new line as a tuple, with the text and the color
        game_msgs.append( (line, color) )

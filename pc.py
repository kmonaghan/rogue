import libtcodpy as libtcod
import characterclass
import baseclasses
import equipment
import messageconsole

player = None

def create_player():
    global player

    #create object representing the player
    fighter_component = characterclass.Fighter(hp=100, defense=10, power=2, xp=0, death_function=player_death)
    player = baseclasses.Character(0, 0, '@', 'player', libtcod.white, blocks=True, fighter=fighter_component)

    player.level = 1

    #initial equipment: a dagger
    obj = equipment.dagger()
    player.add_to_inventory(obj)
    obj.equipment.equip()
    obj.always_visible = True

    player.add_to_inventory(equipment.confusion_scroll())
    player.add_to_inventory(equipment.fireball_scroll())
    player.add_to_inventory(equipment.lighting_scroll())

def player_death(player):
    #the game ended!
    messageconsole.message('You died!', libtcod.red)
    baseclasses.game_state = 'dead'

    #for added effect, transform the player into a corpse!
    player.char = '%'
    player.color = libtcod.dark_red

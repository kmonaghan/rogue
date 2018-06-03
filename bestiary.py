import libtcodpy as libtcod
import baseclasses
import characterclass
import messageconsole
import ai

def goblin(x, y):
    #create a goblin
    fighter_component = characterclass.Fighter(hp=10, defense=0, power=2, xp=50, death_function=monster_death)
    ai_component = ai.BasicMonster()

    colour = libtcod.desaturated_green

    monster = baseclasses.Object(x, y, 'G', 'goblin', colour,
                     blocks=True, fighter=fighter_component, ai=ai_component)

    dice = libtcod.random_get_int(0, 1, 100)

    if (dice >= 99):
        monster.colour = libtcod.silver
        monster.fighter.multiplier = 1.5
        monster.fighter.xp = monster.fighter.xp * 1.5
        monster.loot = equipment.random_magic_weapon()

    return monster

def orc(x, y):
    #create an orc
    fighter_component = characterclass.Fighter(hp=20, defense=1, power=4, xp=35, death_function=monster_death)
    ai_component = ai.BasicMonster()

    colour = libtcod.desaturated_green

    monster = baseclasses.Object(x, y, 'O', 'Orc', colour,
                                    blocks=True, fighter=fighter_component, ai=ai_component)

    dice = libtcod.random_get_int(0, 1, 100)

    if (dice >= 99):
        monster.colour = libtcod.silver
        monster.fighter.multiplier = 1.5
        monster.fighter.xp = monster.fighter.xp * 1.5
        monster.loot = equipment.random_magic_weapon()

    return monster

def troll(x, y):
    #create a troll
    fighter_component = characterclass.Fighter(hp=30, defense=2, power=8, xp=100, death_function=monster_death)
    ai_component = ai.BasicMonster()

    colour = libtcod.darker_green

    monster = baseclasses.Object(x, y, 'T', 'troll', color,
                     blocks=True, fighter=fighter_component, ai=ai_component)

    dice = libtcod.random_get_int(0, 1, 100)

    if (dice >= 99):
        monster.colour = libtcod.silver
        monster.fighter.multiplier = 1.5
        monster.fighter.xp = monster.fighter.xp * 1.5
        monster.loot = equipment.random_magic_weapon()

    return monster

def monster_death(monster):
    #transform it into a nasty corpse! it doesn't block, can't be
    #attacked and doesn't move
    messageconsole.message('The ' + monster.name + ' is dead! You gain ' + str(monster.fighter.xp) + ' experience points.', libtcod.orange)
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()

    if (monster.loot != None):
        loot.x = monster.x
        loot.y = monster.y
        baseclasses.object.append(loot)

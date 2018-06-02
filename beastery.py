import libtcodpy as libtcod
import baseclasses
import characterclass
import messageconsole
import ai

def goblin(x, y):
    #create a goblin
    fighter_component = characterclass.Fighter(hp=10, defense=0, power=2, xp=50, death_function=monster_death)
    ai_component = ai.BasicMonster()

    monster = baseclasses.Object(x, y, 'G', 'goblin', libtcod.darker_green,
                     blocks=True, fighter=fighter_component, ai=ai_component)

    return monster

def orc(x, y):
    #create an orc
    fighter_component = characterclass.Fighter(hp=20, defense=1, power=4, xp=35, death_function=monster_death)
    ai_component = ai.BasicMonster()

    monster = baseclasses.Object(x, y, 'o', 'orc', libtcod.desaturated_green,
                                    blocks=True, fighter=fighter_component, ai=ai_component)

    return monster

def troll(x, y):
    #create a troll
    fighter_component = characterclass.Fighter(hp=30, defense=2, power=8, xp=100, death_function=monster_death)
    ai_component = ai.BasicMonster()

    monster = baseclasses.Object(x, y, 'T', 'troll', libtcod.darker_green,
                     blocks=True, fighter=fighter_component, ai=ai_component)

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

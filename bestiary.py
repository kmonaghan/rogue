import libtcodpy as libtcod
import baseclasses
import characterclass
import messageconsole
import ai
import equipment

def goblin(x, y):
    #create a goblin
    fighter_component = characterclass.Fighter(hp=10, defense=0, power=3, xp=5, death_function=monster_death)
    ai_component = ai.BasicMonster()

    monster = baseclasses.Object(x, y, 'G', 'goblin', libtcod.desaturated_green,
                     blocks=True, fighter=fighter_component, ai=ai_component)

    dice = libtcod.random_get_int(0, 1, 100)

    if (dice >= 98):
        monster.color = libtcod.silver
        monster.fighter.multiplier = 1.5
        monster.fighter.xp = monster.fighter.xp * 1.5
        monster.loot = equipment.random_magic_weapon()

    return monster

def orc(x, y):
    #create an orc
    fighter_component = characterclass.Fighter(hp=20, defense=1, power=4, xp=15, death_function=monster_death)
    ai_component = ai.BasicMonster()

    monster = baseclasses.Object(x, y, 'O', 'Orc', libtcod.light_green,
                                    blocks=True, fighter=fighter_component, ai=ai_component)

    dice = libtcod.random_get_int(0, 1, 100)

    if (dice >= 98):
        monster.color = libtcod.silver
        monster.fighter.multiplier = 1.5
        monster.fighter.xp = monster.fighter.xp * 1.5
        monster.loot = equipment.random_magic_weapon()

    return monster

def troll(x, y):
    #create a troll
    fighter_component = characterclass.Fighter(hp=30, defense=2, power=8, xp=100, death_function=monster_death)
    ai_component = ai.BasicMonster()

    monster = baseclasses.Object(x, y, 'T', 'troll', libtcod.darker_green,
                     blocks=True, fighter=fighter_component, ai=ai_component)

    dice = libtcod.random_get_int(0, 1, 100)

    if (dice >= 98):
        monster.color = libtcod.silver
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
        monster.loot.x = monster.x
        monster.loot.y = monster.y
        baseclasses.objects.append(monster.loot)

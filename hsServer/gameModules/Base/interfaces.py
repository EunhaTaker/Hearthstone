import abc
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(' ')

'''
职业
'''


class Druid:
    profession = 'druid'


class Hunter:
    profession = 'hunter'


class Mage:
    profession = 'mage'


class Paladin:
    profession = 'paladin'


class Priest(abc.ABC):
    profession = 'priest'


class Rogue(abc.ABC):
    profession = 'rogue'


class Shaman:
    profession = 'shaman'


class Warlock(abc.ABC):
    profession = 'warlock'


class Warrior(abc.ABC):
    profession = 'warrior'


class Neutral(abc.ABC):
    profession = 'neutral'


# Professions = [
#     Druid, Hunter, Mage, Paladin, Priest, Rogue, Shaman, Warlock, Warrior,
#     Neutral
# ]
'''
种族
'''


class NonRace(abc.ABC):
    race = ''


class Beast(abc.ABC):
    race = 'beast'


class Dragon:
    rece = 'dragon'


class Elemental:
    race = 'elemental'


class Pirate:
    race = 'pirate'


class Demon(abc.ABC):
    race = 'demon'


class Murloc:
    race = 'murloc'


class Mech(abc.ABC):
    race = 'mech'


class Totem:
    race = 'totem'


class All(Beast, Dragon, Elemental, Pirate, Demon, Murloc, Mech, Totem):
    race = 'all'


'''
稀有度
'''


class Derive:  #衍生卡
    rarity = 'derive'


class Basic:
    rarity = 'basic'


class Common:
    rarity = 'common'


class Rare:
    rarity = 'rare'


class Epic:
    rarity = 'epic'


class Legendary:
    rarity = 'legendary'

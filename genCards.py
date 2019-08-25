# print(__package__,'lalax') #TODO 为何输出3次
# from hsClient.Interface import *
from hsClient.gameModules.Minions import *
from hsClient.gameModules.Spells import *
from hsClient.gameModules.Weapons import *
from hsClient.gameModules.Heros import *
professions = [
    Druid, Hunter, Mage, Paladin, Priest, Rogue, Shaman, Warlock, Warrior,
    Neutral
]
CardsStr = ''
for p in professions:
    ts = list(set(p.__subclasses__()).difference(set(Derive.__subclasses__())))
    ts.sort(key=lambda x: x.cost)
    strs = ""
    for t in ts:
        strs += t.__name__ + ','
    CardsStr += '[' + strs + '],\n'
CardsStr = 'Cards = [' + CardsStr + ']'
importStr = 'from .Minions import *\n'\
            +'from .Spells import *\n'\
            +'from .Heros import *\n'\
            +'from .Weapons import *\n\n'\
            +'openingHeros = [Malfurion, Rexxar, Jaina, Uther, Anduin, Valeera, Thrall, Guldan, Garrosh]\n'
import os
with open(
        f'{os.path.dirname(__file__)}\\hsServer\\gameModules\\Cards4server.py',
        'w') as f:
    f.write(importStr + CardsStr)
importStr = importStr.replace('Server', 'Client')
with open(f'{os.path.dirname(__file__)}/hsClient/gameModules/Cards4client.py',
          'w') as f:
    f.write(importStr + CardsStr)

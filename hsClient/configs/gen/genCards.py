# print(__package__,'lalax') #TODO 为何输出3次
# from ..hsClient.Base import * 
from ..hsClient.Minions import *
from ..hsClient.Spells import *
from ..hsClient.Weapons import *
from ..hsClient.Heros import *
professions = [Druid, Hunter, Mage, Paladin, Priest,
                       Rogue, Shaman, Warlock, Warrior, Neutral]
CardsStr = ''
for p in professions:
    ts = list(set(p.__subclasses__()).difference(set(Derive.__subclasses__())))
    ts.sort(key=lambda x:x.cost)
    strs = ""
    for t in ts:
        strs += t.__name__+','
    CardsStr += '['+strs+'],\n'
CardsStr = 'Cards = ['+CardsStr+']'
importStr = 'from .hsServer.Minions import *\n'\
            +'from .hsServer.Spells import *\n'\
            +'from .hsServer.Heros import *\n'\
            +'from .hsServer.Weapons import *\n\n'\
            +'openingHeros = [Malfurion, Rexxar, Jaina, Uther, Anduin, Valeera, Thrall, Guldan, Garrosh]\n'
with open(f'{__file__}/../../Cards4server.py','w') as f:
    f.write(importStr+CardsStr)
importStr = importStr.replace('Server','Client')
with open(f'{__file__}/../../Cards4client.py','w') as f:
    f.write(importStr+CardsStr)
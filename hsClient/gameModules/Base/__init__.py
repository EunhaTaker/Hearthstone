from .card_base import *
from .minion_base import *
from .spell_base import *
from .weapon_base import *
from .hero_base import *


# 获取一个角色的位置（与服务端约定的），用于传输
def toLocation(card, player):
    #loc1: 0/2为英雄，1/3为随从, 0/1为友方，2/3为敌方
    #loc2: 位置
    loc1 = 0 if card.holder == player else 2
    if isinstance(card, Minion):
        loc1 += 1
        loc2 = card.holder.minionField.index(card)
        loc = (loc1, loc2)
    else:
        loc = (loc1, 0)
    return loc


# 将位置转换为随从
def fromLocation(loc, player):
    loc1, loc2 = loc
    if loc1 >= 2:
        player = player.opponent
    if loc1 % 2 == 0:
        char = player.hero
    else:
        char = player.minionField[loc2]
    return char


# 同类方法合并器
def mergeFunc(*funcs):
    def newFunc(*args):
        for func in funcs:
            func(*args)

    return newFunc

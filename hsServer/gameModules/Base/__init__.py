from .card_base import *
from .minion_base import *
from .spell_base import *
from .weapon_base import *
from .hero_base import *


def toLocation(card, player):
    #0/2为英雄，1/3为随从, 0/1为友方，2/3为敌方
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


class Filter:
    #卡牌筛选器
    def __init__(self):
        print(233)
        #取随从、法术、武器、英雄牌基类的所有子类，但排除它们的衍生牌基类
        self.Cards = set(Minion.__subclasses__() + Spell.__subclasses__() +
                         Weapon.__subclasses__() +
                         Hero.__subclasses__()) ^ set(Derive._subclasses__())

    def filter(self, card, conditions):
        results = set(self.Cards)
        # 过滤每一种条件
        for condition in conditions:
            key = condition['key']
            # 运算符
            operator = condition['operator']
            # 宾语
            obj = condition['object']
            #temp是一种条件的筛选结果
            temp = {}
            # key若为卡牌类型、种族、职业，obj必为相应的类，获取obj所有子类即可
            if key in ['type', 'race', 'profession']:
                temp = obj.__subclass__()
            # 费用
            elif key == 'cost':
                cost = obj
                if operator == '+':
                    cost = type(card).cost + num
                    for Card in results:
                        if Card.cost == cost:
                            temp.add(Card)
                elif operator == '<=':
                    for Card in results:
                        if Card.cost <= cost:
                            temp.add(Card)
                elif operator == '>=':
                    for Card in results:
                        if Card.cost >= cost:
                            temp.add(Card)
            # 效果
            elif key == 'ext':
                for Card in results:
                    if obj in Card.exts:
                        temp.add(Card)
            # 取交集
            results = results.intersection(temp)
        return results

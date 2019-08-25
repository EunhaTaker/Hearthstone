import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(' ')

import abc

from enum import Enum
import random
import copy
deepcopy = copy.deepcopy


class Event(Enum):
    回合开始 = 0
    抽牌 = 1
    弃牌 = 31
    打出 = 2
    召唤 = 3
    施放前 = 4
    施放后 = 5
    放置奥秘 = 6
    揭示奥秘 = 7
    装备 = 8
    摧毁 = 9
    治疗 = 10
    受治疗 = 11
    受伤 = 12
    造成伤害 = 30
    死亡 = 13
    攻击 = 14
    受攻击 = 15
    英雄技能 = 16
    回合结束 = 20


class Target(Enum):
    #4位分别为：友、敌、随从、英雄
    #通过&排除获得角色代码
    不限 = 0b1111
    友方 = 0b1011
    敌方 = 0b0111
    随从 = 0b1110
    英雄 = 0b1101


class Role(Enum):
    #4位分别为：友、敌、随从、英雄
    友方 = 0b1000
    敌方 = 0b0100
    随从 = 0b0010
    英雄 = 0b0001


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


filter = None
#进化
# adaptions = {
#     '+3攻击力': (3, 0),
#     '+3生命值': (0, 3),
#     '获得+1/+1': (1, 1),
#     '圣盾': 'shield',
#     '风怒': 'windfury',
#     '嘲讽': 'taunt',
#     '魔免': 'magicAvoid',
#     '剧毒': 'poisonous',
#     #匿名函数真难用
#     '直到你的下个回合，获得潜行': lambda m: m.exts.add('stealth') and m.holder.tiggerField.append(\
#         lambda event, char=None, n=0:  event==Event.回合开始 and m.holder.myTurn and  m.exts.remove('stealth'))],
#     '亡语：召唤两个1/1的植物': lambda m: deathrattle = lambda : plant= m.derive()


class Card:

    exts = []
    targetType = []

    def __init__(self, holder=None):
        self.holder = holder  #用于衍生卡，普通卡牌在getDrawed认主
        #是否可操作
        self.available = False

    def getTargets(self, role):
        targets = []
        roleCode = 0b1111
        for r in role:
            roleCode &= r.value
        players = []
        if roleCode & 0b1000:
            players.append(self.holder)
        if roleCode & 0b0100:
            players.append(self.holder.opponent)
        for p in players:
            if roleCode & 0b0010:
                targets += p.minionField
            if roleCode & 0b0001:
                targets.append(p)
        return targets

    #合并多个参数相似的方法，返回一个新方法
    def mergeFunction(self, *funcs):
        #定义新方法
        def func(*args):
            #执行funcs所有方法
            for f in funcs:
                f(*args)

        #返回新方法
        return func

    #被抽到
    def getDrawed(self, player):
        player.hand.append(self)
        # card = copy.deepcopy(self)
        # player.temphand.append(card)
        self.holder = player

    # 产生一个无holder副本
    def getTempCopy(self):
        tempcard = deepcopy(self)
        tempcard.holder = None
        return tempcard

    #询问是否可操作
    def ask(self):
        #消耗不超过资源
        self.available = (self.cost <= self.holder.mana)

    #打出
    def play(self, target):
        # 消耗法力值
        self.holder.modCrystal(dMana=self.cost)
        # handIdx = self.holder.hand.index(self)
        # tempcard = self.holder.temphand.pop(handIdx)
        self.holder.hand.remove(self)
        tempcard = self.getTempCopy()
        self.holder.opponent.args.append(tempcard)
        target = [target] if target else []
        if 'battlecry' in self.exts:
            self.battlecry(*target)
        if 'combo' in self.exts and self.holder.comboCount > 0 and self.type != 'spell':
            self.combo(*target)

    # 打出后
    def afterPlay(self):
        self.holder.genEvent(Event.打出, self)

    #造成伤害
    def dealDamage(self, char, amount):
        if amount <= 0:
            return
        #调用受伤方法，获得最终伤害值
        damage = char.survive(amount, 'poisonous' in self.exts)
        if 'lifesteal' in self.exts:
            #吸血
            self.restore(damage)
        self.holder.genEvent(Event.造成伤害, self, damage)

    #恢复生命值
    def restore(self, character, amount):
        character.health = min(character.health + amount, character.life)

    def summonDerive(self, minion, bfriend=True):
        ## 召唤衍生随从
        if bfriend:
            player = self.holder
        else:
            player = self.holder.opponent
        minion.holder = player
        # myIndex = self.holder.minionField.index(self)
        minion.summon(len(player.minionField))


class Minion(Card):
    type = 'minion'

    def __init__(self, holder=None):
        super().__init__(holder)
        #是否在战场
        self.onField = False
        #攻击机会(上场不能立即攻击)
        self.attackChance = 0
        #已攻击次数
        self.attackCount = 0
        # 被冻结
        self.freezed = False
        #无敌
        self.invincible = False
        # #buff
        # self.buffs = {'attack': 0, 'life': 0}
        # 光环列表：攻击力，生命值，其他
        self.halos = {'attack': 0, 'life': 0}
        #生命值
        self.health = self.life
        # 死亡的（用于剧毒）
        self.dead = False

    # 询问是否可攻击或打出
    def ask(self):
        if self.onField:  # 在场上
            #有攻击机会&未被冻结->可操作
            self.available = (self.attackChance > 0 and not self.freezed)
        else:  # 在手牌
            super().ask()
            #场上无空位->不可操作
            if len(self.minionField) >= self.holder.minionCeiling:
                self.available = False

    # 光环改变属性
    def getHalo(self, key, delta):
        self.halos[key] += delta
        if key == 'attack':
            self.attack += delta
        if key == 'life':
            self.life += delta
            self.health += delta

    def play(self, fieldIdx, target=None):
        # self.holder.opponent.args.append(se)
        super().play(target)
        self.summon(fieldIdx)
        self.afterPlay()

    # 召唤
    def summon(self, fieldIdx=-1):
        #初始化生命值
        self.health = self.life
        #设为在场
        self.onField = True
        #生成召唤事件
        self.holder.genEvent(Event.召唤, self)
        # 入场
        self.enter(fieldIdx)

    # 入场
    def enter(self, fieldIdx=-1):
        if fieldIdx == -1:
            fieldIdx = len(self.holder.minionField)
        # 安装触发器
        if 'tigger' in self.exts:
            self.holder.battle.tiggerField.append(self.tigger)
        # 放入战场
        self.holder.minionField.insert(fieldIdx, self)
        self.holder.battle.allminions.append(self)
        # 处理光环
        if 'halo' in self.exts:
            if 'minion' in self.haloTypes:
                self.holder.haloChars['minion'].append(self)
                for minion in self.holder.battle.allminions:
                    self.halo(minion)
            if 'player' in self.haloTypes:
                # self.holder.haloChars['player'].append(self)
                self.halo()
            if 'hand' in self.haloTypes:
                self.holder.haloChars['hand'].append(self)
                for card in self.holder.hand + self.holder.opponent.hand:
                    self.halo(card)
        # 接受光环
        for hm in self.holder.haloChars[
                'minion'] + self.holder.opponent.haloChars['minion']:
            hm.halo(self)
        # 处理冲锋
        if 'charge' in self.exts:
            # 处理风怒
            self.attackChance = 2 if 'windfury' in self.exts else 1
        else:
            self.attackChance = 0

    # 离场
    def leave(self):
        #卸载触发器
        if 'tigger' in self.exts:
            self.holder.battle.tiggerField.remove(self.tigger)
        # 卸载光环
        if 'halo' in self.exts:
            self.dehalo()
        # 撤销光环加成
        for hm in self.holder.haloChars[
                'minion'] + self.holder.opponent.haloChars['minion']:
            hm.dehalo(self)
        #撤除战场
        self.holder.minionField.remove(self)
        self.holder.battle.allminions.remove(self)

    def die(self):
        #生成死亡事件
        self.holder.genEvent(Event.死亡, self)
        # 加入持有者的坟场
        self.holder.graveyard.append(type(self))
        self.leave()
        if 'deathrattle' in self.exts:
            self.deathrattle()

    #进攻
    def attacking(self, character):
        self.holder.genEvent(Event.攻击, self)
        # 实际伤害，反伤，剧毒 <- 受攻击
        damageAmount, backDamage, poisonous = character.getAttacked(self)
        #应处理吸血
        if backDamage > 0:
            self.survive(backDamage, poisonous)
        self.attackChance -= 1
        self.attackCount += 1

    def getAttacked(self, char):  # 受攻击
        self.holder.genEvent(Event.受攻击, self)
        # damage = char.calDamage()
        damage = char.attack
        poisonous = 'poisonous' in char.exts
        damage = self.survive(damage, poisonous)
        return damage, self.attack, 'poisonous' in self.exts

    #受到伤害
    def survive(self, damage, poisonous=False):
        if 'shield' in self.exts:
            damage = 0
            self.exts.remove('shield')
        else:
            self.health -= damage
            self.holder.genEvent(Event.受伤, self, damage)
            if poisonous:
                # 设为中毒
                self.dead = True
        return damage

    def calDamage(self):
        return self.attack


class Spell(Card):
    blocked = False

    def play(self, target=None):
        super().play(None)
        self.holder.genEvent(Event.施放前, self)
        #可能被对手反制
        #TODO 服务端available待完成
        if self.blocked:
            return
        target = [target] if target else []
        self.cast(*target)
        if 'echo' in self.exts:
            s = type(self)()
            s.holder = self.holder
            s.exts.append('temporary')
        self.afterPlay()

    def cast(self, target=None):
        # 最好是重载方法调用完再调用
        if 'tigger' in self.exts:
            self.holder.battle.tiggerField.append(self.tigger)
        # 事件
        self.holder.genEvent(Event.施放后, self)

    def rmTigger(self):
        # self.holder.secrets.append(self.tigger)
        idx = self.holder.battle.tiggerField.index(self.tigger)
        # 所有一次性触发器，触发完毕会置自己为None，便于清理
        self.holder.battle.tiggerField[idx] = None


class Secret(Spell):
    exts = ['secret']


# 伤害法术接口
class DamageSpell:
    def calSpellDamage(self, dmg):
        return dmg + self.holder.spellDmgAdd

    def dealDamage(self, tgt, dmg):
        dmg = self.calSpellDamage(dmg)
        return super().dealDamage(tgt, dmg)

    def cast(self, tgt):
        self.dealDamage(tgt, self.damage)
        super().cast()


class Hero(Card):
    def __init__(self):
        super().__init__()
        self.freezed = False  # 被冻结

    def getAttacked(self, damage):  # 受攻击
        self.holder.life -= damage
        return damage, 0


class Weapon(Card):
    type = 'weapon'

    def __init__(self, cost, attack, durability):
        super().__init__(cost)
        self.attack = attack
        self.durability = durability

    def equip(self):
        if self.holder.weapon:  # 摧毁原武器（如果有）
            self.holder.weapon.destory()
        self.holder.weapon = self  # 装备这把武器
        self.battlecry()  # 触发战吼

    def getDamage(self, character):
        #应考虑光环
        self.durability -= 1
        if self.durability <= 0:
            self.destory()

    def destory(self):
        #应生成摧毁事件
        self.deathrattle()


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


Professions = [
    Druid, Hunter, Mage, Paladin, Priest, Rogue, Shaman, Warlock, Warrior,
    Neutral
]
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

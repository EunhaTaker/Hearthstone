# from .functions import logger, toLocation, fromLocation, mergeFunc
from .enums import Event, Target, Role
from .interfaces import *


import copy
deepcopy = copy.deepcopy



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

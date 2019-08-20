from ..Interface import *

class BooldmageThalnos(Minion, Neutral, NonRace, Legendary):
    name = '血法师萨尔诺斯'
    desc = '法术伤害+1，亡语：抽一张牌'
    exts = ['deathrattle', 'halo']
    haloTypes = ['player']
    cost, attack, life = 2,1,1

    def deathrattle(self):
        self.holder.drawCard()

    def halo(self, char=None):
        if not char:
            self.holder.spellDmgAdd += 1

    def dehalo(self):
        self.holder.spellDmgAdd -= 1

class GrimPatron(Minion, Neutral, NonRace, Rare):
    name = '奴隶主'
    desc = '每当该随从收到伤害并没有死亡，召唤另一个奴隶主'
    cost, attack, life = 5,3,3

    def survive(self, amount, poisonous):
        super().survive(amount, poisonous)
        if self.life>0:
            newMe = GrimPatron()
            self.derive(newMe)
        

class MecHaroo(Minion, Neutral, Mech, Common):
    name = '机械袋鼠'
    desc = '亡语：召唤一个1/1的机器人'
    exts = ['deathrattle']
    cost, attack, life = 1,1,1

    def deathrattle(self):
        son = JoE_Bot(self.holder)
        son.summon()

class JoE_Bot(Minion, Neutral, Mech, Derive):
    name = '机器人'
    cost, attack, life =1,1,1


class IronbeakOwl(Minion, Neutral, Beast, Common):
    name = '铁嘴猫头鹰'
    desc = '战吼：沉默一个随从'
    exts = ['battlecry']
    targetType = [Target.随从]
    cost, attack, life = 3,2,1

    def battlecry(self, char):
        #卸载触发器
        if 'tigger' in char.exts:
            local.battle.tiggerField.remove(char.tigger)
        Card = type(char)
        self.setAttr(atk=Card.attack, life=Card.life)
        #清理效果及buff
        char.exts = []
        char.buffs = []


class Pig(Minion, Neutral, Beast, Basic):
    name = '野猪'
    desc = '冲锋'
    exts = ['charge']
    cost, attack, life = 1,1,1

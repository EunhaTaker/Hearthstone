from ..Interface import *

# 初始英雄继承衍生类，避免列入卡牌列表

class Malfurion(Hero, Druid, Derive):
    name = '玛法里奥'
    def power(self):
        self.holder.attack += 1
        self.holder.armor += 1

class Rexxar(Hero, Hunter, Derive):
    name = '雷克萨'
    def power(self):
        # TODO伤害来源是英雄还是玩家？
        self.dealDamage(self.holder.opponent.hero, 2)

class Jaina(Hero, Mage, Derive):
    name = '吉安娜'
    def power(self, target):
        self.dealDamage(target, 1)

class Uther(Hero, Paladin, Derive):
    name = '乌瑟尔'
    def power(self):
        s = SilverHandRecruit()
        self.summonDerive(s)

class SilverHandRecruit(Minion, Paladin, Derive):
    name = '白银之手新兵'
    cost, attack, life = 1, 1, 1

class Anduin(Hero, Priest, Derive):
    name = '安度因'
    def power(self, character=None):
        #考虑治疗光环
        amount = 2
        self.restore(character, amount)


class Valeera(Hero, Rogue, Derive):
    name = '瓦莉拉'
    def power(self, character=None):
        dagger = Weapon(self.holder, 1, 1, 2)
        self.holder.equip(dagger)

class Thrall(Hero, Shaman, Derive):
    name = '萨尔'
    def power(self):
        import random
        totem = [SearingTotem, HealingTotem, WrathOfAirTotem, StoneclawTotem]
        t = random.choice(totem)()
        self.summonDerive(t)

class SearingTotem(Minion):
    name = '灼热图腾'
    cost, attack, life = 1,1,1

class HealingTotem(Minion, Shaman, Derive):
    name = '治疗图腾'
    cost, attack, life = 1, 0, 2

    def tigger(self, event, char=None, amount=0):
        if event == Event.回合结束 and self.holder.myTurn:
            for char in self.holder.minionField+[self.holder.hero]:
                self.restore(char, 1)

class WrathOfAirTotem(Minion, Shaman, Derive):
    name = '空气之怒图腾'
    exts = ['halo']
    cost, attack, life = 1, 0, 2
    haloTypes = ['player']

    def halo(self, char=None):
        if not char:
            self.holder.spellDamage += 1

    def dehalo(self):
        self.holder.spellDamage -= 1

class StoneclawTotem(Minion, Shaman, Derive):
    name = '石爪图腾'
    exts = ['taout']
    cost, attack, life = 1,0,2

class Guldan(Hero, Warlock, Derive):
    name = '古尔丹'
    def power(self, character=None):
        self.dealDamage(self, 2)
        self.holder.drawCard()

class Garrosh(Hero, Warrior, Derive):
    name = '加尔鲁什'
    def power(self):
        self.holder.armor += 2
        

from ..Interface import *


class Coin(Spell, Neutral, Derive):
    name = '幸运币'
    cost = 0

    def cast(self):
        print('cast')
        if self.holder.modCrystal(dMana=1, dCrystal=1):
            self.exts = ['tigger']
        super().cast()

    def tigger(self, event, character=None, amount=None):
        if event == Event.回合结束:
            self.holder.modCrystal(-1)
            self.rmTigger()


class Claw(Spell, Druid, Common):
    name = '爪击'
    cost = 1
    def cast(self):
        self.holder.attack += 2
        self.holder.armor += 2

class Moonfire(DamageSpell, Spell, Druid, Common):
    name = '月火术'
    cost = 0
    damage = [1]

    def cast(self, target):
        self.dealDamage(target, self.damage)

class ArcaneShot(DamageSpell, Spell, Hunter, Basic):
    name = '奥术射击'
    desc = '造成{dmg}点伤害'
    cost = 1
    damage = 2

class Countspell(Secret, Spell, Mage, Basic):
    name = '法术反制'
    cost = 3

    def tigger(self, event, char, amount=0):
        if event==Event.施放前 and char.holder != self.holder:
            char.available = False
            super().tigger()
            return True

class DeadlyPoison(Spell, Rogue, Basic):
    name = '毒药'
    cost = 1

    def ask(self):
        if not self.player.weapon:
            self.available = False

    def play(self):
        self.player.weapon.attack += 2


class Eviscerate(DamageSpell, Spell, Rogue, Common):
    name = '刺骨'
    exts = ['combo']
    cost = 2
    targetType = [Target.不限]
    damage = [2,4]

    def cast(self, target):
        damage = self.damage[1] if self.holder.comboCount > 0 else self.damage[1]
        self.dealDamege(target, damage)

# class UnstableEvolution(Spell, Shaman, Epic):
#     name = '不稳定的异变'
#     cost = 1
#     targetType = [Target.友方, Target.随从]
#     exts = ['echo']

#     def cast(self, char):
#         pass

class Defile(DamageSpell, Spell, Warlock, Rare):
    name = '亵渎'
    desc = "对所有随从造成{dmg}点伤害，如果有随从死亡，再次施放该法术"
    cost = 2
    damage = 1

    def cast(self, count=0):
        for m in self.holder.battle.allminions:
            self.dealDamage(m, self.damage)
        # 若有随从死亡，且施放次数不足14
        if self.holder.clear() and count < 14:
            if count==0:
                self.holder.autoPlay = True
            defile = Defile(self.holder)
            defile.cast(count+1)
            if count==0:
                self.holder.autoPlay = False
        super(DamageSpell, self).cast()

class Treachery(Spell, Warlock, Epic):
    name = '变节'
    desc = '选择一个友方随从，将控制权交给你的对手'
    targetCode = [Target.友方, Target.随从]
    cost = 3

    def ask(self):
        if not self.holder.minionField:
            self.available = False

    def cast(self, minion):
        self.holder = self.holder.opponent
        
Spells = [Defile, Treachery]



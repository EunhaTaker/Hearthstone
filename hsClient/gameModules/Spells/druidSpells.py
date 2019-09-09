from ..Base import *

class Coin(Spell, Neutral, Derive):
    name = '幸运币'
    desc = '本回合增加一点法力值'
    cost = 0

    def cast(self):
        if self.holder.modCrystal(1, 1):
            self.exts = ['tigger']
        super().cast()
    
    def tigger(self, event, character=None, amount=None):
        if event == Event.回合结束:
            self.holder.modCrystal(0, -1)
            self.rmTigger()

class Claw(Spell, Druid, Common):
    name = '爪击'
    desc = '使你的英雄本回合中获得+2攻击力，+2护甲值'
    cost = 1

    def cast(self):
        self.holder.attack += 2
        self.holder.armor += 2

class Moonfire(DamageSpell, Spell, Druid, Common):
    name = '月火术'
    desc = '造成{dmg}点伤害'
    cost = 0
    damage = 1

    def cast(self, target):
        self.dealDamage(target, self.damage)

class ArcaneShot(DamageSpell, Spell, Hunter, Basic):
    name = '奥术射击'
    desc = '造成{dmg}点伤害'
    cost = 1
    damage = 2

class Countspell(Secret, Spell, Mage, Basic):
    name = '法术反制'
    desc = '奥秘：你的对手打出一个法术时，反制该法术'
    cost =3

    def tigger(self, event, char, amount=0):
        if event == Event.施放前 and char.holder != self.holder:
            char.available = False
            return True

class DeadlyPoison(Spell, Rogue, Basic):
    name = '毒药'
    desc = '使你的武器获得+2攻击力'
    cost = 1

    def ask(self):
        super().ask()
        if not self.player.weapon:
            self.available = False

    def cast(self):
        self.player.weapon.attack += 2

class Eviscerate(DamageSpell, Spell, Rogue, Common):
    name = '刺骨'
    desc = '造成{dmg}点伤害，连击：造成{dmg}点伤害'
    exts = ['combo']
    damage = [2, 4]
    cost = 2

    def cast(self, target):
        damage = self.damage[1] if self.holder.comboCount > 0 else self.damage[1]
        self.dealDamege(target, damage)

class Defile(DamageSpell, Spell, Warlock, Rare):
    name = '亵渎'
    desc = "对所有随从造成一点伤害，如果有随从死亡，再次施放该法术"
    cost = 2
    damage = 1

    def cast(self, count=0):
        for m in local.battle.allminions:
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

    def play(self, minion):
        self.holder = self.holder.opponent
        #TODO 变位置动画


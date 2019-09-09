from ..Base import *

class Gorehowl(Weapon, Warrior, Epic):
    name = '血吼'
    desc = '当你攻击随从时，不损失耐久度，转为减少一点攻击力'
    cost, attack, durability = 7,7,1

    def getDamage(self, character):
        #应考虑光环
        if isinstance(character, Minion):
            self.attack -= 1
        else:
            self.durability -= 1
            if self.durability <= 0:
                self.destory()

from ..Interface import *

class Gorehowl(Weapon, Warrior, Epic):
    cost, attack, durability = 7, 7, 1

    def getDamage(self, character):
        #应考虑光环
        if isinstance(character, Minion):
            self.attack -= 1
        else:
            self.durability -= 1
            if self.durability <= 0:
                self.destory()

if __name__ == '__main__':
    filter = Filter()
    from Minions import KoblodBarbarian
    k = KoblodBarbarian()
    l=filter.filter(k, [['cost','+',1]])
    print(l)

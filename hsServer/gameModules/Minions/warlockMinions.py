from ..Interface import *

class Howlfiend(Minion, Warlock, Demon, Common):
    name = '咆哮魔'
    desc = '每当该随从受到一点伤害，弃一张牌'
    cost, attack, life = 3,3,6

    def survive(self, amount, poisonous=False):
        super().survive(amount, poisonous)
        self.holder.discard()


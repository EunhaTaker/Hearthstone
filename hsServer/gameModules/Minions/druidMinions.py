from ..Interface import *

class Acornbearer(Minion, Druid, NonRace, Common):
    name = '橡树果实能力者'
    desc = '将两个1/1的松鼠加入你的手牌'
    cost, attack, life = 1, 2, 1

    def deathrattle(self):
        for i in range(2):
            squirrel = Squirrel()
            squirrel.getDrawed(self.holder)

class Squirrel(Minion, Druid, Beast, Derive):
    name = '松鼠'
    cost, attack, life = 1, 1, 1




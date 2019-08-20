from ..Interface import *

class MurlocKnight(Minion, Paladin, Murloc, Common):
    name='鱼人骑士'
    desc = '激励：随机召唤一个鱼人'
    exts = ['tigger']
    cost, attack, life = 4,3,4

    def tigger(self, event, char=None, amount=0):
        if event == Event.英雄技能 and char == self.holder:
            murlocs = Murloc.__subclasses__()
            murlocs = list(set(murlocs).difference(set(Derive.__subclasses__())))
            murloc = self.holder.getRand(murlocs)[0]
            self.summonDerive(murloc)

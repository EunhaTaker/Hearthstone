from ..Interface import *

class MurlocKnight(Minion, Paladin, Murloc, Common):
    name='鱼人骑士'
    desc = '激励：随机召唤一个鱼人'
    exts = ['tigger']
    cost, attack, life = 4,3,4

    def tigger(self, event, char=None, amount=0):
        if event == Event.英雄技能 and char == self.holder:
            murloc = local.args.pop(0)()
            self.derive(murloc)

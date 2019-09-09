from ..Base import *

class KoblodBarbarian(Minion, Warrior, NonRace, Rare):
    name = '狗头人兵'
    desc = '你的回合开始时，随机攻击一个敌人'
    exts = ['tigger']
    cost, attack, life =3,4,4

    def tigger(self, event, character=None, amount=None):
        enemys=self.getTargets([Target.敌方])
        enemy = self.holder.getRand(enemys)
        self.attacking(enemy)

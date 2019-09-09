from ..Base import *

class KoblodBarbarian(Minion, Warrior, NonRace, Rare):
    name = '狗头人兵'
    desc = '你的回合开始时，随机攻击一个敌人'
    exts = ['tigger']
    cost, attack, life =3,4,4

    def tigger(self, event, character=None, amount=0):
        if event == Event.回合开始:
            character = self.request(self, 'tigger')
            self.attacking(character) #TODO随机攻击

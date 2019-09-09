from ..Base import *

class NorthShireCleric(Minion, Priest, NonRace, Basic):
    name = '北郡牧师'
    desc = '每当有随从受到治疗，抽一张牌'
    cost, attack, life = 1,1,3

    def tigger(self, event, character, amount):
        if event == Event.受治疗 and character.holder.getRole(character)&Target.随从:
            self.holder.drawCard()

class Chameleos(Minion, Priest, NonRace, Legendary):
    name = '变色龙'
    cost, attack, life = 1,1,1
    copyfrom = None

    def getDrawed(self, player):
        super().__init__(player)
        self.holder.battle.tiggerField.append(self.tigger)

    def summon(self, fieldIdx):
        if self.copyfrom:
            # 深复制，召唤复制而不是自己
            copy = deepcopy(self.copyfrom)
            copy.holder = self.holder
            copy.summon(fieldIdx)
        else:
            super().summon(fieldIdx)
        self.holder.battle.tiggerField[self.holder.battle.tiggerField.index(self.tigger)] = None

    def tigger(self, event, char, amount=0):
        if event==Event.回合开始 and char==self.holder:
            self.copyfrom = self.holder.getRand(self.holder.hand, 1, public=False)
            self.holder.args.append(copyfrom.getTempCopy())
            
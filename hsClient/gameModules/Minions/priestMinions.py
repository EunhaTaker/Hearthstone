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
    desc = '你的回合开始时，随机变成一个对手手牌的复制'
    cost, attack, life = 1, 1, 1
    copyfrom = None

    def getDrawed(self, player):
        super().__init__(player)
        local.battle.tiggerField.append(self.tigger)

    def summon(self, fieldIdx):
        # TODO 自身消失动画
        if self.copyfrom:
            # 深复制，召唤复制而不是自己
            self.copyfrom.summon(fieldIdx)
        else:
            super().summon(fieldIdx)
        local.battle.tiggerField[local.battle.tiggerField.index(
            self.tigger)] = None

    def tigger(self, event, char, amount=0):
        if event == Event.回合开始 and char == self.holder:
            self.copyfrom = local.args.pop(0)
            # TODO改变外形

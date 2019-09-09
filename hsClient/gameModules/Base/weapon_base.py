from .card_base import *

class Weapon(Card):
    type = 'weapon'

    # def __init__(self, player, cost, attack, durability):
    #     super().__init__()
    #     self.attack = attack
    #     self.durability = durability

    def initImage(self):
        super().initImage()
        self.attack += 0
        self.durability += 0

    def equip(self):
        if self.holder.weapon:  # 摧毁原武器（如果有）
            self.holder.weapon.destory()
        self.holder.weapon = self  # 装备这把武器
        self.battlecry()  # 触发战吼

    def getDamage(self, character):
        #应考虑光环
        self.durability -= 1
        if self.durability <= 0:
            self.destory()

    def destory(self):
        #应生成摧毁事件
        self.deathrattle()


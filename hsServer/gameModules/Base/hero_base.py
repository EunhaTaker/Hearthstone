from .card_base import *


class Hero(Card):
    def __init__(self):
        super().__init__()
        self.freezed = False  # 被冻结

    def getAttacked(self, damage):  # 受攻击
        self.holder.life -= damage
        return damage, 0

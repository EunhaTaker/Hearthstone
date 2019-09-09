from .card_base import *

class Spell(Card):
    blocked = False

    def play(self, target=None):
        super().play(None)
        self.holder.genEvent(Event.施放前, self)
        #可能被对手反制
        #TODO 服务端available待完成
        if self.blocked:
            return
        target = [target] if target else []
        self.cast(*target)
        if 'echo' in self.exts:
            s = type(self)()
            s.holder = self.holder
            s.exts.append('temporary')
        self.afterPlay()

    def cast(self, target=None):
        # 最好是重载方法调用完再调用
        if 'tigger' in self.exts:
            self.holder.battle.tiggerField.append(self.tigger)
        # 事件
        self.holder.genEvent(Event.施放后, self)

    def rmTigger(self):
        # self.holder.secrets.append(self.tigger)
        idx = self.holder.battle.tiggerField.index(self.tigger)
        # 所有一次性触发器，触发完毕会置自己为None，便于清理
        self.holder.battle.tiggerField[idx] = None


class Secret(Spell):
    exts = ['secret']


# 伤害法术接口
class DamageSpell:
    def calSpellDamage(self, dmg):
        return dmg + self.holder.spellDmgAdd

    def dealDamage(self, tgt, dmg):
        dmg = self.calSpellDamage(dmg)
        return super().dealDamage(tgt, dmg)

    def cast(self, tgt):
        self.dealDamage(tgt, self.damage)
        super().cast()

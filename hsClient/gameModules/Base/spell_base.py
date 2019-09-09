from .card_base import *

class Spell(Card):
    type = 'spell'
    blocked = False

    def play(self, target=None):
        super().play(None)
        self.holder.spellUse(self)
        self.holder.genEvent(Event.施放前, self)
        local.battleScene.remove(self)
        if self.blocked:
            return
        target = [target] if target else []
        self.cast(*target)
        self.afterPlay()

    def cast(self, target=None):
        #最好是重载方法调用完再调用
        if 'tigger' in self.exts:
            local.battle.tiggerField.append(self.tigger)
        #事件
        self.holder.genEvent(Event.施放后, self)

    def rmTigger(self):
        #法术tigger通常为一次性
        # self.holder.rmTiggers.append(self.tigger)
        idx = local.battle.tiggerField.index(self.tigger)
        # 所有一次性触发器，触发完毕会置自己为None，便于清理
        local.battle.tiggerField[idx] = None


# 奥秘接口
class Secret:
    exts = ['secret']


# 伤害法术接口
class DamageSpell:
    def updateDesc(self):
        if isinstance(self.damage, int):
            damage = [self.damage]
        else:
            damage = []
            for dmg in self.damage:
                damage.append(self.calSpellDamage(dmg))
        logger.info('更新法术描述')
        super().updateDesc(damage=damage)

    def calSpellDamage(self, dmg):
        return dmg + self.holder.spellDmgAdd

    def dealDamage(self, tgt, dmg):
        dmg = self.calSpellDamage(dmg)
        print('法伤super', super())
        return super().dealDamage(tgt, dmg)

    def cast(self, tgt):
        self.dealDamage(tgt, self.damage)
        super().cast()

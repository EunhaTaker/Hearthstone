from .card_base import *

class Minion(Card):
    type = 'minion'

    def __init__(self, holder=None):
        super().__init__(holder)
        #是否在战场
        self.onField = False
        #攻击机会(上场不能立即攻击)
        self.attackChance = 0
        #已攻击次数
        self.attackCount = 0
        # 被冻结
        self.freezed = False
        #无敌
        self.invincible = False
        # #buff
        # self.buffs = []
        # 光环列表：攻击力，生命值，其他
        self.halos = [0, 0]
        # 死亡的（用于剧毒）
        self.dead = False

    #绘制
    def initImage(self):
        super().initImage()
        # x, y = local.winWidth/2, local.winHeight/2
        x, y = 0, 0
        items = self.items
        # 利用__setattr__绘制攻击力和生命值
        self.attack += 0
        self.health = self.life
        #种族背景
        if self.race:
            items['racebg'] = Sprite(local.res['m_race'], scale=scale)
            items['racebg'].do(RotateBy(1, duration=0))
            items['race'] = Label(self.race,
                                  font_name='Belwe Bd BT',
                                  font_size=30 * scale,
                                  anchor_x='center',
                                  anchor_y='center')
            self.add(self.items['racebg'], z=1.25)
            print(self.items['racebg'])
            self.add(self.items['race'], z=1.3)
            items['racebg'].position = (x + 28 * scale, y - 252 * scale)
            items['race'].position = (x + 26 * scale, y - 256 * scale)

    def ask(self):
        #在场上
        if self.onField:
            #有攻击机会&未被冻结->可操作
            self.available = (self.attackChance > 0 and not self.freezed)
        else:
            super().ask()
            #场上无空位->不可操作
            if len(self.holder.minionField) >= local.minionCeiling:
                self.available = False

    def play(self, fieldIdx, target=None):
        super().play(target)
        self.summon(fieldIdx)
        self.afterPlay()

    # 召唤
    def summon(self, fieldIdx=-1):
        if fieldIdx == -1:
            local.battleScene.add(self)
        # 初始化生命值
        self.health = self.life
        # 设为在场
        self.onField = True
        # 入场
        self.enter(fieldIdx)
        # 生成召唤事件
        self.holder.genEvent(Event.召唤, self)

    # 入场
    def enter(self, fieldIdx=-1):
        if fieldIdx == -1:
            fieldIdx = len(self.holder.minionField)
        # 安装触发器
        if 'tigger' in self.exts:
            local.battle.tiggerField.append(self.tigger)
        # 放入战场
        self.holder.minionField.insert(fieldIdx, self)
        local.battle.allminions.append(self)
        # 动画
        self.holder.renderMinionField()
        # 处理光环
        if 'halo' in self.exts:
            if 'minion' in self.haloTypes:
                self.holder.haloChars['minion'].append(self)
                for minion in local.battle.allminions:
                    self.halo(minion)
            if 'player' in self.haloTypes:
                # self.holder.haloChars['player'].append(self)
                self.halo()
            if 'hand' in self.haloTypes:
                self.holder.haloChars['hand'].append(self)
                for card in self.holder.hand:  #ps:由于对方手牌不可见，本客户端无视之
                    self.halo(card)
        # 接受光环
        for hm in self.holder.haloChars[
                'minion'] + self.holder.opponent.haloChars['minion']:
            hm.halo(self)
        # 处理冲锋
        if 'charge' in self.exts:
            # 处理风怒
            self.attackChance = 2 if 'windfury' in self.exts else 1
        else:
            self.attackChance = 0

    # 离场
    def leave(self):
        #卸载触发器
        if 'tigger' in self.exts:
            local.battle.tiggerField.remove(self.tigger)
        # 卸载光环
        if 'halo' in self.exts:
            if 'minion' in self.haloTypes:
                self.holder.haloChars['minion'].append(self)
                for minion in self.holder.battle.allminions:
                    self.dehalo(minion)
            if 'player' in self.haloTypes:
                # self.holder.haloChars['player'].append(self)
                self.dehalo()
            if 'hand' in self.haloTypes:
                self.holder.haloChars['hand'].append(self)
                for card in self.holder.hand + self.holder.opponent.hand:
                    self.dehalo(card)
        # 撤销光环加成
        for hm in self.holder.haloChars[
                'minion'] + self.holder.opponent.haloChars['minion']:
            hm.dehalo(self)
        #撤除战场
        self.holder.minionField.remove(self)
        local.battle.allminions.remove(self)
        #动画
        self.holder.renderMinionField()

    def die(self):
        #生成死亡事件
        self.holder.genEvent(Event.死亡, self)
        # 加入持有者的坟场
        self.holder.graveyard.append(type(self))
        # 离场
        self.leave()
        #TODO 卡牌碎裂动画
        local.battleScene.remove(self)
        if 'deathrattle' in self.exts:
            self.deathrattle()

    def attacking(self, character):
        self.holder.genEvent(Event.攻击, self)
        # 实际伤害，反伤，剧毒 <- 受攻击
        damageAmount, backDamage, poisonous = character.getAttacked(self)
        #应处理吸血
        if backDamage > 0:
            self.survive(backDamage, poisonous)
        self.attackChance -= 1
        self.attackCount += 1

    def getAttacked(self, char):
        ## 被攻击
        self.holder.genEvent(Event.受攻击, self)
        # damage = char.calDamage()
        damage = char.attack
        poisonous = 'poisonous' in char.exts
        damage = self.survive(damage, poisonous)
        return damage, self.attack, 'poisonous' in self.exts

    def survive(self, damage, poisonous=False):
        if 'shield' in self.exts:
            damage = 0
            self.exts.remove('shield')
            #消除圣盾动画
        else:
            self.health -= damage
            self.holder.genEvent(Event.受伤, self, damage)
            if poisonous:
                # 设为中毒
                self.dead = True
        return damage

from .Interface import *
import _thread
import copy

import time


class Player(cocos.layer.Layer):
    def __init__(self, hero, isOpponent):
        self.hand = []  #手牌
        self.weapon = None  #武器
        self.hero = hero  #英雄
        hero.holder = self
        self.minionField = []  # 随从场
        self.secretField = []  #奥秘场
        self.graveyard = []  #坟场
        local.battle.tiggerField.append(self.tigger)  # 触发器场
        self.haloChars = {'minion': [], 'player': [], 'hand': []}  # 光环角色
        self.myTurn = False  # 我的回合
        self.turnRange = []  #回合轮转安排，默认为空
        self.attackChance = 1  # 攻击机会
        self.comboCount = 0  # 本回合连击数
        self.life = self.health = 30
        self.attack = 0  # 英雄裸攻
        self.armor = 0  #护甲值
        self.spellDmgAdd = 0  #法术伤害
        self.crystal = 0  #法力水晶
        self.mana = 0  #法力值
        self.locks = 0  #被锁水晶数
        self.opponent = None  #对手对象
        self.autoPlay = False  #自动施放期间
        self.initRender(isOpponent)
        self.invincible = False     #无敌

    def getAvailables(self):
        cards = []
        for card in self.hand + self.minionField:
            card.ask()
            if card.available:
                cards.append(card)
                card.add(card.items['circle'])
        return cards

    #让对方打出时，让对方player（也就是self）执行这个方法，用于模拟对方的出牌操作（因为对方打出之前是未知的）
    def play(self):
        print(local.args)
        args = local.args.pop(0)
        card = local.args.pop(0)
        card.holder = self
        card.getDrawed(self)
        handIdx = args.pop(0)
        sprite = self.hand.pop(handIdx)
        self.remove(sprite)
        card.position = sprite.position
        card.play(*args)

    def tigger(self, event, char=None, amount=1):
        if event == Event.打出 and self.myTurn:
            self.comboCount += 1
        elif event == Event.回合开始:
            if self.myTurn:
                if self.isMe:
                    print('我的回合开始')
                self.drawCard()
                char = self
                # 增长水晶并补充法力值
                self.modCrystal(dMana=0, dCrystal=1, restore=True)
                # 为随从补满攻击机会
                for m in self.minionField:
                    m.attackChance = 3 if 'superwindfury' in m.exts else 2 if 'windfury' in m.exts else 1
            else:
                if self.isMe:
                    print('敌方回合开始')
                char = self.opponent
        elif event == Event.回合结束:
            if self.myTurn:
                if self.isMe:
                    print('我的回合结束')
                # 处理冻结
                for char in self.minionField:
                    # 攻击次数置0
                    char.attackCount = 0
                    # 若被冻结且剩余攻击机会，则解除冻结
                    if char.freezed and char.attackChance:
                        char.freezed = False
                        #TODO解除冻结动画
                # 攻击机会属于玩家，受冻结属于英雄，这里特殊处理
                if self.attackChance and self.hero.freezed:
                    self.hero.freezed = False
                    #TODO解除冻结动画
                self.comboCount = 0
            else:
                if self.isMe:
                    print('敌方回合结束')

            #TODO水晶变化动画
        elif event == Event.回合结束:
            if self.myTurn:
                self.attack = 0

    def getRole(self, character):
        role = 0b1010  # 初始化为友方随从
        if character.holder != self:
            role ^= 0b1100
        if isinstance(character, Hero):
            role ^= 0b0011
        return role

    def calDamage(self):  #计算自己的伤害
        return self.attack + self.weapon.attack

    def attacking(self, character):
        #此前应确认是否可攻击
        damage = self.calDamage()
        damageAmount, backDamage = character.getAttacked(damage)  # 获得反击伤害
        #应处理吸血
        self.getAttacked(backDamage)
        if self.weapon:
            self.weapon.getDamage(character)

    def getAttack(self, damage):
        #应考虑光环
        if self.armor >= damage:
            self.armor -= damage
        else:
            self.hero.life -= damage - self.armor
            self.armor = 0
        return damage, self.attack

    def genEvent(self, event: Event, char=None, amount=1):  # 生成事件并触发触发器
        if self.autoPlay and event in [Event.打出, Event.施放前, Event.施放后]:
            return
        for tigger in local.battle.tiggerField:
            tigger(event, char, amount)
        # 清理失效触发器
        while None in local.battle.tiggerField:
            local.battle.tiggerField.remove(None)

    # 抽牌
    def drawCard(self, amount=1):
        if self.isMe:
            for i in range(amount):
                print('卡牌列表', local.args, i)
                card = local.args.pop(0)
                if type(card) == int:
                    # TODO疲劳
                    pass
                elif len(self.hand) >= local.handCeiling:
                    # TODO爆牌动画
                    break
                #产生抽牌事件
                self.genEvent(Event.抽牌)
                #卡牌的被抽到方法
                card.getDrawed(self)
            self.renderHand()
        else:
            #作为敌方玩家时的抽牌逻辑
            for i in range(amount):
                cardBack = Sprite(local.res['cardBack'],
                                  position=(local.winWidth * 1.1,
                                            local.winHeight * 0.5))
                cardBack.scale = local.itemScale
                self.hand.append(cardBack)
                self.add(cardBack)
                # TODO敌方疲劳
                if len(self.hand) >= local.handCeiling:
                    # TODO爆牌动画
                    break
                #产生抽牌事件
                self.genEvent(Event.抽牌)
            self.renderHand()

    def discard(self, amount=1):  #弃牌
        cardIdxs = local.args.pop(0)
        if not cardIdxs:
            return
        for idx in cardIdxs:
            c = self.hand.pop(idx)
            action = MoveBy((0, 0.5*local.winHeight), 1)
            _thread.start_new_thread(self.maintainAnime, (1, ))
            c.do(action)
            try:
                local.battleScene.remove(c)
            except:
                logger.error('scene无法删除该sprite')
        self.renderHand()
        self.genEvent(Event.弃牌, self, amount)
        

    def initRender(self, isOpponent):
        super().__init__()
        local.battleScene.add(self)
        # TODO 绘制双方英雄
        self.crystalSprites = []
        if isOpponent:
            self.isMe = False
            self.handRegion = local.enemyHandRegion
            self.minionRegion = local.enemyMinionRegion
            self.crystalRegion = local.enemyCrystalRegion
        else:
            self.isMe = True
            self.handRegion = local.myHandRegion
            self.minionRegion = local.myMinionRegion
            self.crystalRegion = local.myCrystalRegion

    def log(self):
        print('手牌：', end="")
        for c in self.hand:
            print(c.name, end=" ")
        print('\n随从：', end='')
        for c in self.minionField:
            print(c.name, end=" ")
        print()

    #清算
    def clear(self):
        deads = []
        print('行动后，清算')
        for m in local.battle.allminions:
            if m.health <= 0 or m.dead:
                deads.append(m)
        if deads:
            for dead in deads:
                dead.die()
            # 重新绘制随从区
            self.renderMinionField()
            self.opponent.renderMinionField()
            # 新生儿死亡处理
            self.clear()
            return True

    #绘制手牌区
    def renderHand(self):
        px, py, w, h = self.handRegion
        ncard = len(self.hand)
        interval = w / (ncard + 1)
        y = py + h / 2
        _thread.start_new_thread(self.maintainAnime, (1, ))
        for card in self.hand:
            i = self.hand.index(card) + 1
            card.scale = local.cardScale
            action = MoveTo((px + interval * i, y), 1)
            card.do(action)

    def spellUse(self, spell):
        _thread.start_new_thread(self.maintainAnime, (1.5, ))
        spell.do(MoveTo((-50, local.winHeight / 2), 1.5))

    #绘制随从区
    def renderMinionField(self):
        px, py, w, h = self.minionRegion
        ncard = len(self.minionField)
        interval = w / (ncard + 1)
        y = py + h / 2
        _thread.start_new_thread(self.maintainAnime, (1, ))
        for card in self.minionField:
            i = self.minionField.index(card) + 1
            card.scale = local.cardScale
            action = MoveTo((px + interval * i, y), 1)
            card.do(action)

    #为动画延时
    def maintainAnime(self, duration):
        local.animingMutex += duration
        time.sleep(duration)
        local.animingMutex -= duration

    #改变水晶或法力值
    def modCrystal(self, dMana=0, dCrystal=0, restore=False):
        # 法力水晶溢出，flag置为False
        flag = True
        px, py, w, h = self.crystalRegion
        x0 = px + w / 2
        y0 = py + h / (local.MaxCrystal * 2)
        scale = h / local.MaxCrystal
        if dCrystal:
            if dCrystal > 0:
                for i in range(dCrystal):
                    # 水晶不得超过上限
                    if self.crystal == local.MaxCrystal:
                        flag = False
                        break
                    # 捏个空水晶
                    empty = Sprite(local.res['empty_crystal'],
                                   position=(x0, y0 + scale * self.crystal))
                    # 捏个水晶
                    mana = Sprite(local.res['crystal'],
                                  position=(x0, y0 + scale * self.crystal))
                    # 保存
                    self.crystalSprites.append((empty, mana))
                    self.add(empty)
                    # 修改数值
                    self.crystal += 1
            else:
                # 删减水晶和法力值
                children = self.get_children()
                for item in self.crystalSprites[dCrystal:]:
                    self.crystalSprites.remove(item)
                    self.remove(item[0])
                    self.crystal -= 1
                    if item[1] in children:
                        self.remove(item[1])
        if dMana:
            if dMana < 0:
                for item in self.crystalSprites[self.mana + dMana:self.mana]:
                    self.remove(item[1])
            else:
                for item in self.crystalSprites[self.mana:self.mana + dMana]:
                    self.add(item[1], z=0.1)
            self.mana += dMana
        elif restore:
            # 补满法力值
            if self.mana < self.crystal - self.locks:
                for item in self.crystalSprites[self.mana:self.crystal -
                                                self.locks]:
                    self.add(item[1], z=0.1)
            else:
                # 补满后法力值可能比之前少（过载太多）
                for item in self.crystalSprites[self.crystal -
                                                self.locks:self.mana]:
                    self.remove(item[1])
            self.mana = self.crystal - self.locks
            self.locks = 0
        return flag

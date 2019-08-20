from .Interface import *
from copy import deepcopy
import random

class Deck(list):   #继承list

    def __init__(self):
        super().__init__()
        self.triedCount = 0

    def draw(self):  #抽牌
        if self:
            return super().pop()
        else:
            self.triedCount += 1
            return self.triedCount

    def shuffleIn(self, cards): #洗入卡牌
        self.extend(cards)
        random.shuffle(self)

    def range(self, cards): #安排牌库
        self.clear()
        self.extend(cards)
        random.shuffle(self)

    def destroy(self, amount=0, scale=0): #按数量或比例摧毁牌库
        cards = []
        num = (amount and min(amount, len(self))) or len(self)*scale//1
        for i in range(num):
            cards.append(self.draw())
        return cards

    def open(self, amount): #安排起始手牌
        return self.destroy(amount)

    def replace(self, cards, repIdxs): #换牌
        newCards = self.destroy(amount=len(repIdxs))
        for idx in repIdxs:
            self.shuffleIn([cards[idx]])
            cards[idx] = newCards[repIdxs.index(idx)]
        return newCards

class Player:

    def __init__(self, battle, hero):
        self.hand = [] # 手牌
        # self.temphand = []  # 无holder版
        self.deck = Deck()              # 牌库
        self.hero = hero                # 英雄
        hero.holder = self
        self.weapon = None              # 武器
        self.minionField = []           # 随从场
        self.secretField = []           # 奥秘场
        self.graveyard = []             # 坟场
        self.battle = battle            # 公共战场信息
        battle.tiggerField.append(self.tigger)  # 触发器场
        self.haloChars = {'minion':[], 'player':[], 'hand':[]}  #光环角色
        self.myTurn = False             # 我的回合
        self.turnRange = []             # 回合轮转安排，默认为空
        self.attackChance = 1           # 攻击机会
        self.comboCount = 0             # 本回合连击数
        self.life = self.health = 30
        self.attack = 0                 #英雄裸攻
        self.spellDmgAdd = 0               #法术伤害
        self.armor = 0                  #护甲值
        self.crystal = 0                #法力水晶
        self.mana = 0                   #法力值
        self.locks = 0                  #被锁水晶

        self.opponent = None    #对手对象
        self.autoPlay = False   #自动施放期间
        self.args = []  #传给客户端的参数序列
        self.sleeptime = 0  #播放动画的时间
        self.secrets = []   #该玩家再这个元过程触发的奥秘

    def log(self):
        print('手牌：',end="")
        for c in self.hand:
            print(c.name, end=" ")
        print('\n随从：',end='')
        for c in self.minionField:
            print(c.name, end=" ")
        print()
    
    #清算
    def clear(self):
        deads = []
        for m in self.battle.allminions:
            if m.health <= 0 or m.dead:
                deads.append(m)
        if deads:
            for dead in deads:
                dead.die()
            # 新生儿死亡处理
            self.clear()
            return True

    def tigger(self, event, char=None, amount=1):
        if event == Event.打出 and char==self:
            self.comboCount += 1
        elif event == Event.回合开始:
            if char.crystal < 10:
                char.crystal += 1
                char.mana = char.crystal-char.locks
                char.locks = 0
            if self.myTurn:
                self.drawCard()
                #为随从补满攻击机会
                for m in self.minionField:
                    m.attackChance = 3 if 'superwindfury' in m.exts else 2 if 'windfury' in m.exts else 1
        elif event == Event.回合结束:
            if self.myTurn:
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
                # 玩家攻击力置为0
                self.attack = 0
                self.comboCount=0

    def getRole(self, character):
        role = Target.不限  # 0b1111
        if character.holder != self:
            role &= Target.敌方
        else:
            role &= Target.友方
        if isinstance(character, Hero):
            role &= Target.英雄
        else:
            role &= Target.随从
        return role

    def getRand(self, seq, amount=1, public=True):
        seq = seq[:]
        random.shuffle(seq)
        result = seq[:amount]
        self.args.append(result)
        # 公开信息
        if public:
            self.opponent.args.append(result)
        return result

    def calDamage(self):    #计算自己的伤害
        return self.attack+self.weapon.attack

    #改变水晶或法力值
    def modCrystal(self, dMana=0, dCrystal=0, restore=False):
        # 法力水晶溢出，flag置为False
        flag = True
        if dCrystal:
            self.crystal += dCrystal
            if self.crystal>10:
                self.crystal = 10
                flag = False
            if self.mana>self.crystal:
                self.mana = self.crystal
        if dMana:
            self.mana += dMana
        elif restore:
            # 补满法力值
            self.mana = self.crystal-self.locks
            self.locks = 0
        return False

    def discard(self, amount=1):    #弃牌
        cardIdxs = self.getRand(list(range(len(self.hand))), amount)
        if not cardIdxs:
            return
        for idx in cardIdxs:
            c = self.hand.pop(idx)
            print('弃',c.name)
        self.genEvent(Event.弃牌, self, amount)

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

    # def post(self, obj):
    #     copys = []
    #     if isinstance(obj, list):
    #         for card in obj:
    #             copy = deepcopy(card)
    #             copy.holder = None
    #             copys.append(copy)
    #     self.args.append(copys)

    def genEvent(self, event, char=None, amount=1):  # 生成事件并触发触发器
        if self.autoPlay and event in [Event.打出, Event.施放前, Event.施放后]:
            return
        for tigger in self.battle.tiggerField:
            # if tigger:
            tigger(event, char, amount)
        # 清理过期触发器
        while None in self.battle.tiggerField:
            self.battle.tiggerField.remove(None)

    #抽牌
    def drawCard(self, amount=1):
        # cards = []
        for i in range(amount):
            #从牌库顶抽取
            card = self.deck.draw()
            if type(card) == int:  # 疲劳
                #TODO
                pass
            elif len(self.hand)>=10:#local.handCeiling: #爆牌
                break
            #复制一份无holder版本
            tempcard = deepcopy(card)
            self.args.append(tempcard)
            # cards.append(tempcard)
            #产生抽牌事件
            self.genEvent(Event.抽牌, card)
            #卡牌的被抽到方法
            card.getDrawed(self)
        logger.info('筹拍：%s',self.args)

            
            


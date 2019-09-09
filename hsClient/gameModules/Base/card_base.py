# from .functions import logger, toLocation, fromLocation, mergeFunc
from .enums import Event, Target, Role
from .interfaces import *
from .. import local
import random, re

import cocos
from cocos.actions import *
director = cocos.director.director
Sprite = cocos.sprite.Sprite
Label = cocos.text.Label
scene = cocos.scene

scale = local.itemScale

class Card(cocos.cocosnode.CocosNode):
    desc = ''
    exts = []
    targetType = []

    def __init__(self, holder=None):
        self.holder = holder  #用于衍生卡，普通卡牌在getDrawed认主
        #是否可操作
        self.available = False
        #绘制
        self.initImage()

    # 绘制
    def initImage(self):
        # 初始英雄无需绘制卡牌
        if self.type == 'hero' and isinstance(self, Derive):
            return
        super().__init__()
        #初始位置在窗口右侧
        # self.position = local.winWidth*0.6, 0
        self.position = local.winWidth * 1.1, local.winHeight * 0.5
        ##贴图, 文本
        self.items = {}
        items = self.items
        #随从、法术、武器、英雄 标识符
        typeCode = self.type[0] + '_'
        #牌框
        frame = Sprite(local.res[typeCode + self.profession])
        items['frame'] = frame
        # frame.card = self   #用于battle从点击获取卡牌
        self.add(frame, z=1)
        #横幅
        items['ribbon'] = Sprite(local.res[typeCode + 'ribbon'])
        self.add(items['ribbon'], z=1.2)
        #稀有度宝石
        if self.rarity not in ['basic', 'derive']:
            items['gem'] = Sprite(local.res[typeCode + self.rarity])
            self.add(items['gem'], z=1.1)
        #费用背景
        items['costbg'] = Sprite(local.res['mana'])
        self.add(items['costbg'], z=1.1)
        #传说装饰
        if self.rarity == 'legendary':
            self.items['dragon'] = Sprite(local.res['m_dragon'])
            self.add(self.items['dragon'], z=1.2)
        #集体缩放
        for s in items.values():
            s.scale = scale
        #表示可操作的光圈（初始不显示）
        items['circle'] = Sprite(local.res['available'], scale=scale * 1.3)
        #名称
        items['name'] = Label(self.name,
                              bold=True,
                              font_name='Microsoft Yahei',
                              font_size=8 * scale,
                              anchor_x='center',
                              anchor_y='baseline',
                              dpi=300)
        self.add(items['name'], z=1.3)
        items['name'].do(Rotate(-7, duration=0))
        #描述
        self.updateDesc()
        #费用
        items['cost'] = Label(str(self.cost),
                              font_name='Belwe Bd BT',
                              font_size=57.5 * scale,
                              anchor_x='center',
                              anchor_y='baseline')
        self.add(items['cost'], z=1.3)
        #位置修正
        x, y = 0, 0
        items['frame'].position = x, y
        items['ribbon'].position = (x + 12.5 * scale, y - 25 * scale)
        if items.get('gem'):
            items['gem'].position = (x + 12 * scale, y - 58 * scale)
        items['costbg'].position = (x - 60 * scale, y + 250 * scale)
        if items.get('dragon'):
            items['dragon'].position = (x + 70 * scale, +250 * scale)
        items['name'].position = (x, y - 25 * scale)
        for desc in items['desc']:
            desc.position = (x, y - 120 * scale -
                             items['desc'].index(desc) * 40 * scale)
        items['cost'].position = (x - 162.5 * scale, y + 227.5 * scale)
        items['circle'].position = (x, y + 10 * scale)
        self.scale = local.cardScale

    # 更新描述
    def updateDesc(self, damage=None):
        desc = self.desc
        if damage:
            for dmg in damage:
                # 对多处伤害进行解析
                arr = desc.partition('{dmg}')
                desc = arr[0] + str(dmg) + arr[2]
        if self.items.get('desc'):
            for item in self.items['desc']:
                # 清除原描述
                self.remove(item)
        numPline = local.descLen1Line  #每行字数
        nlines = (len(desc) + numPline - 1) // numPline
        descs = []
        if nlines >= 1:
            # 建立新描述
            for i in range(nlines):
                if i == nlines - 1:
                    text = desc[i * numPline:]
                else:
                    text = desc[i * numPline:(i + 1) * numPline]
                descLabel = Label(text,
                                  color=(0, 0, 0, 255),
                                  font_name='Microsoft Yahei',
                                  font_size=6 * scale,
                                  anchor_x='center',
                                  anchor_y='center',
                                  dpi=300)
                descs.append(descLabel)
                self.add(descLabel, z=1.3)
        self.items['desc'] = descs

    # 属性变化带动数值显示变化
    def __setattr__(self, name, value):
        if name == "health":
            if value == self.life:
                color = (0, 200, 10,
                         255) if self.life > type(self).life else (255, 255,
                                                                   255, 255)
            else:
                color = (255, 0, 0, 255)
            if self.items.get('life'):
                self.remove(self.items['life'])
            self.items['life'] = Label(str(value),
                                       color=color,
                                       font_name='Belwe Bd BT',
                                       font_size=55 * scale,
                                       anchor_x='center',
                                       anchor_y='baseline')
            self.add(self.items['life'], z=1.3)
            self.items['life'].position = (190 * scale, -290 * scale)
        elif name == "attack":
            if value > type(self).attack:
                color = (0, 200, 10, 255)
            else:
                color = (255, 255, 255, 255)
            if self.items.get('attack'):
                self.remove(self.items['attack'])
            self.items['attack'] = Label(str(value),
                                         color=color,
                                         font_name='Belwe Bd BT',
                                         font_size=55 * scale,
                                         anchor_x='center',
                                         anchor_y='baseline')
            self.add(self.items['attack'], z=1.3)
            self.items['attack'].position = (-160 * scale, -290 * scale)
        if name == "durability":
            if value == self.durability:
                color = (0, 200, 10,
                         255) if self.durability > type(self).durability else (
                             255, 255, 255, 255)
            else:
                color = (255, 0, 0, 255)
            if self.items.get('durability'):
                self.remove(self.items['durability'])
            self.items['durability'] = Label(str(value),
                                             color=color,
                                             font_name='Belwe Bd BT',
                                             font_size=55 * scale,
                                             anchor_x='center',
                                             anchor_y='baseline')
            self.add(self.items['durability'], z=1.3)
            self.items['durability'].position = (190 * scale, -290 * scale)
        super().__setattr__(name, value)

    # 粗略获取目标列表
    def getTargets(self, role=None):
        if not role:
            role = self.targetType
            if not role:
                return None
        targets = []
        roleCode = 0b1111
        for r in role:
            roleCode &= r.value
        players = []
        #友方
        if roleCode & Role.友方.value:
            players.append(self.holder)
        #敌方
        if roleCode & Role.敌方.value:
            players.append(self.holder.opponent)
        for p in players:
            #随从
            if roleCode & 0b0010:
                targets += p.minionField
            #英雄
            if roleCode & 0b0001:
                targets.append(p.hero)
        return targets

    # 获得所有可针对的目标
    def getSelectables(self):
        #TODO 处理无敌对象
        if self in self.holder.hand:
            #若为手牌
            targets = self.getTargets()
            if targets == None:
                return None
            if self.type == 'spell':
                #法术牌需排除魔免、潜行目标
                for c in targets:
                    if set(c.exts).intersection({'magicAvoid', 'stealth'}):
                        targets.remove(c)
        else:
            #若自己是场上随从，目标锁定为敌方角色
            targets = self.getTargets([Target.敌方])
            taouts = []  # 存放嘲讽随从
            for c in targets:  #剔除英雄再轮询
                # 排除潜行目标
                if 'stealth' in c.exts:
                    targets.remove(c)
                # 潜行会掩盖嘲讽
                elif 'taout' in c.exts:
                    taouts.append(c)
            # 若敌方有嘲讽，目标改为所有嘲讽随从
            if taouts:
                targets = taouts
        return targets

    #被抽到
    def getDrawed(self, player):
        #绘制
        self.initImage()
        local.battleScene.add(self)
        player.hand.append(self)
        self.holder = player

    # 询问是否可操作
    def ask(self):
        #消耗不超过资源
        self.available = (self.cost <= self.holder.mana)

    # 打出
    def play(self, target):
        # 消耗法力值
        self.holder.modCrystal(dMana=-self.cost)
        self.holder.hand.remove(self)
        self.holder.renderHand()
        # 战吼和连击
        target = [target] if target else []
        if 'battlecry' in self.exts:
            self.battlecry(*target)
        if 'combo' in self.exts and self.holder.comboCount > 0 and self.type != 'spell':
            self.combo(*target)

    # 打出后
    def afterPlay(self):
        # 生成打出事件
        self.holder.genEvent(Event.打出, self)

    # 造成伤害
    def dealDamage(self, char, amount):
        if amount <= 0:
            return
        #调用受伤方法，获得最终伤害值
        damage = char.survive(amount, 'poisonous' in self.exts)
        if 'lifesteal' in self.exts:
            #吸血
            self.restore(self, damage)
        self.holder.genEvent(Event.造成伤害, self, damage)

    # 治疗
    def restore(self, character, amount):
        character.health = min(character.health + amount, character.life)

    def summonDerive(self, minion, bfriend=True):
        ## 召唤衍生随从
        if bfriend:
            player = self.holder
        else:
            player = self.holder.opponent
        minion.holder = player
        # myIndex = self.holder.minionField.index(self)
        minion.summon(len(player.minionField))

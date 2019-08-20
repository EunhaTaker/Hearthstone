import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(' ')    #filename filemode format

import abc
from enum import Enum
import random, re
from functools import reduce
import cocos
from cocos.actions import *
director = cocos.director.director
Sprite = cocos.sprite.Sprite
Label = cocos.text.Label
scene = cocos.scene
from . import local


class Event(Enum):
    回合开始 = 0
    抽牌 = 1
    弃牌 = 31
    打出 = 2
    召唤 = 3
    施放前 = 4
    施放后 = 5
    放置奥秘 = 6
    揭示奥秘=7
    装备 = 8
    摧毁 = 9
    治疗 = 10
    受治疗 = 11
    受伤 = 12
    造成伤害 = 30
    死亡 = 13
    攻击 = 14
    受攻击 = 15
    英雄技能 = 16
    回合结束 = 20

class Target(Enum):
    #4位分别为：友、敌、随从、英雄
    #通过&排除获得角色代码
    不限 = 0b1111
    友方 = 0b1011
    敌方 = 0b0111
    随从 = 0b1110
    英雄 = 0b1101

class Role(Enum):
    #4位分别为：友、敌、随从、英雄
    友方 = 0b1000
    敌方 = 0b0100
    随从 = 0b0010
    英雄 = 0b0001

# 获取一个角色的位置（与服务端约定的），用于传输
def toLocation(card, player):
    #loc1: 0/2为英雄，1/3为随从, 0/1为友方，2/3为敌方
    #loc2: 位置
    loc1 = 0 if card.holder == player else 2
    if isinstance(card, Minion):
        loc1 += 1
        loc2 = card.holder.minionField.index(card)
        loc = (loc1, loc2)
    else:
        loc = (loc1, 0)
    return loc

# 将位置转换为随从
def fromLocation(loc, player):
    loc1, loc2 = loc
    if loc1>=2:
        player = player.opponent
    if loc1%2==0:
        char = player.hero
    else:
        char = player.minionField[loc2]
    return char

# 同类方法合并器
def mergeFunc(*funcs):
    def newFunc(*args):
        for func in funcs:
            func(*args)
    return newFunc

scale = local.itemScale
class Card(cocos.cocosnode.CocosNode):
    desc = ''
    exts = []
    targetType = []
    def __init__(self, holder=None):
        self.holder = holder    #用于衍生卡，普通卡牌在getDrawed认主
        #是否可操作
        self.available = False
        #绘制
        self.initImage()
    
    # 绘制
    def initImage(self):
        # 初始英雄无需绘制卡牌
        if self.type=='hero' and isinstance(self, Derive):
            return
        super().__init__()
        #初始位置在窗口右侧
        # self.position = local.winWidth*0.6, 0
        self.position = local.winWidth*1.1, local.winHeight*0.5
        ##贴图, 文本
        self.items = {}
        items = self.items
        #随从、法术、武器、英雄 标识符
        typeCode = self.type[0]+'_'
        #牌框
        frame = Sprite(local.res[typeCode+self.profession])
        items['frame'] = frame  
        # frame.card = self   #用于battle从点击获取卡牌
        self.add(frame, z=1)
        #横幅
        items['ribbon'] = Sprite(local.res[typeCode+'ribbon'])
        self.add(items['ribbon'], z=1.2)
        #稀有度宝石
        if self.rarity not in ['basic', 'derive']:
            items['gem'] = Sprite(local.res[typeCode+self.rarity])
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
        items['circle'] = Sprite(local.res['available'], scale=scale*1.3)
        #名称
        items['name'] = Label(self.name,bold=True,
                              font_name='Microsoft Yahei', font_size=8*scale,
                              anchor_x='center', anchor_y='baseline',dpi=300)
        self.add(items['name'], z=1.3)
        items['name'].do(Rotate(-7, duration=0))
        #描述
        self.updateDesc()
        #费用
        items['cost'] = Label(str(self.cost),
                              font_name='Belwe Bd BT', font_size=57.5*scale,
                              anchor_x='center', anchor_y='baseline')
        self.add(items['cost'], z=1.3)
        #位置修正
        x,y=0,0
        items['frame'].position = x,y
        items['ribbon'].position = (x+12.5*scale, y-25*scale)
        if items.get('gem'):
            items['gem'].position = (x+12*scale, y-58*scale)
        items['costbg'].position = (x-60*scale, y+250*scale)
        if items.get('dragon'):
            items['dragon'].position = (x+70*scale, +250*scale)
        items['name'].position = (x, y-25*scale)
        for desc in items['desc']:
            desc.position = (
                x, y-120*scale-items['desc'].index(desc)*40*scale)
        items['cost'].position = (x-162.5*scale, y+227.5*scale)
        items['circle'].position = (x, y+10*scale)
        self.scale = local.cardScale

    # 更新描述
    def updateDesc(self, damage=None):
        desc = self.desc
        if damage:
            for dmg in damage:
                # 对多处伤害进行解析
                arr = desc.partition('{dmg}')
                desc = arr[0]+str(dmg)+arr[2]
        if self.items.get('desc'):
            for item in self.items['desc']:
                # 清除原描述
                self.remove(item)
        numPline = local.descLen1Line   #每行字数
        nlines = (len(desc)+numPline-1)//numPline
        descs = []
        if nlines>=1:
            # 建立新描述
            for i in range(nlines):
                if i == nlines-1:
                    text = desc[i*numPline:]
                else:
                    text = desc[i*numPline:(i+1)*numPline]
                descLabel = Label(text,color=(0,0,0,255),
                                font_name='Microsoft Yahei', font_size=6*scale,
                                anchor_x='center', anchor_y='center', dpi=300)
                descs.append(descLabel)
                self.add(descLabel, z=1.3)
        self.items['desc'] = descs    

    # 属性变化带动数值显示变化
    def __setattr__(self, name, value):
        if name == "health":
            if value == self.life:
                color = (0, 200, 10, 255) if self.life > type(
                    self).life else (255, 255, 255, 255)
            else:
                color = (255, 0, 0, 255)
            if self.items.get('life'):
                self.remove(self.items['life'])
            self.items['life'] = Label(str(value), color=color,
                                       font_name='Belwe Bd BT', font_size=55*scale,
                                       anchor_x='center', anchor_y='baseline')
            self.add(self.items['life'], z=1.3)
            self.items['life'].position = (190*scale, -290*scale)
        elif name == "attack":
            if value > type(self).attack:
                color = (0, 200, 10, 255)
            else:
                color = (255,255,255,255)
            if self.items.get('attack'):
                self.remove(self.items['attack'])
            self.items['attack'] = Label(str(value), color=color,
                                         font_name='Belwe Bd BT', font_size=55*scale,
                                         anchor_x='center', anchor_y='baseline')
            self.add(self.items['attack'], z=1.3)
            self.items['attack'].position = (-160*scale, -290*scale)
        if name == "durability":
            if value == self.durability:
                color = (0, 200, 10, 255) if self.durability > type(
                    self).durability else (255, 255, 255, 255)
            else:
                color = (255, 0, 0, 255)
            if self.items.get('durability'):
                self.remove(self.items['durability'])
            self.items['durability'] = Label(str(value), color=color,
                                       font_name='Belwe Bd BT', font_size=55*scale,
                                       anchor_x='center', anchor_y='baseline')
            self.add(self.items['durability'], z=1.3)
            self.items['durability'].position = (190*scale, -290*scale)
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
            if targets==None:
                return None
            if self.type=='spell':
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
        self.available = (self.cost<=self.holder.mana)

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
        if 'combo' in self.exts and self.holder.comboCount > 0 and self.type!='spell':
            self.combo(*target)

    # 打出后
    def afterPlay(self):
        # 生成打出事件
        self.holder.genEvent(Event.打出, self)

    # 造成伤害
    def dealDamage(self, char, amount):
        if amount<=0:
            return
        #调用受伤方法，获得最终伤害值
        damage = char.survive(amount, 'poisonous' in self.exts)
        if 'lifesteal' in self.exts:
            #吸血
            self.restore(self, damage)
        self.holder.genEvent(Event.造成伤害, self, damage)

    # 治疗
    def restore(self, character, amount):
        character.health = min(character.health+amount, character.life)

    def summonDerive(self, minion, bfriend=True):
        ## 召唤衍生随从
        if bfriend:
            player = self.holder
        else:
            player = self.holder.opponent
        minion.holder = player
        # myIndex = self.holder.minionField.index(self)
        minion.summon(len(player.minionField))


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
        #buff
        # self.buffs = []
        # 死亡的（用于剧毒）
        self.dead = False
        # 光环列表：攻击力，生命值，其他
        self.halos = [0, 0]

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
            items['racebg'] = Sprite(
                local.res['m_race'], scale=scale)
            items['racebg'].do(RotateBy(1,duration=0))
            items['race'] = Label(self.race,
                                  font_name='Belwe Bd BT', font_size=30*scale,
                                  anchor_x='center', anchor_y='center')
            self.add(self.items['racebg'], z=1.25)
            print(self.items['racebg'])
            self.add(self.items['race'], z=1.3)
            items['racebg'].position = (x+28*scale, y-252*scale)
            items['race'].position = (x+26*scale, y-256*scale)

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
        if fieldIdx==-1:
            local.battleScene.add(self)
        #初始化生命值
        self.health = self.life
        #生成召唤事件
        self.holder.genEvent(Event.召唤, self)
        #设为在场
        self.onField = True
        # 入场
        self.enter(fieldIdx)

    # 入场
    def enter(self, fieldIdx=-1):
        if fieldIdx==-1:
            fieldIdx = len(self.holder.minionField)
        # 安装触发器
        if 'tigger' in self.exts:
            local.battle.tiggerField.append(self.tigger)
        # 放入战场
        self.holder.minionField.insert(fieldIdx, self)
        local.battle.allminions.append(self)
        #动画
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
                for card in self.holder.hand:   #ps:由于对方手牌不可知，客户端无视之
                    self.halo(card)
        # 接受光环
        for hm in self.holder.haloChars['minion']+self.holder.opponent.haloChars['minion']:
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
            self.dehalo()
        # 撤销光环加成
        self.halos = [(0, 0)]
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
        if backDamage>0:
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
        return dmg+self.holder.spellDmgAdd

    def dealDamage(self, tgt, dmg):
        dmg = self.calSpellDamage(dmg)
        print('法伤super',super())
        return super().dealDamage(tgt, dmg)

    def cast(self, tgt):
        self.dealDamage(tgt, self.damage)
        super().cast()

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

        
class Hero(Card):
    type = 'hero'

    def __init__(self):
        super().__init__()
        self.freezed = False    #被冻结

    def getAttacked(self, damage):  # 受攻击
        self.holder.life -= damage
        return damage, 0
    

'''
职业
'''
class Druid:
    profession = 'druid'
class Hunter:
    profession = 'hunter'
class Mage:
    profession = 'mage'
class Paladin:
    profession = 'paladin'
class Priest(abc.ABC):
   profession = 'priest'
class Rogue(abc.ABC):
    profession = 'rogue'
class Shaman:
    profession = 'shaman'
class Warlock(abc.ABC):
    profession = 'warlock'
class Warrior(abc.ABC):
    profession = 'warrior'
class Neutral(abc.ABC):
    profession = 'neutral'
'''
种族
'''
class NonRace(abc.ABC):
    race = ''
class Beast(abc.ABC):
    race = 'beast'
class Dragon:
    rece = 'dragon'
class Elemental:
    race = 'elemental'
class Pirate:
    race = 'pirate'
class Demon(abc.ABC):
    race ='demon'
class Murloc:
    race = 'murloc'
class Mech(abc.ABC):
    race ='mech'
class Totem:
    race = 'totem'
class All(Beast, Dragon, Elemental, Pirate, Demon, Murloc, Mech, Totem):
    race = 'all'
'''
稀有度
'''
class Derive:   #衍生卡
    rarity = 'derive'
class Basic:
    rarity ='basic'
class Common:
    rarity ='common'
class Rare:
    rarity ='rare'
class Epic:
    rarity ='epic'
class Legendary:
    rarity ='legendary'

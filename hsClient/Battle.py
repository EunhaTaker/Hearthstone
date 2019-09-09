import _thread

import simuInput
from gameModules.Base import *
from Connect import Connect
from gameModules.Cards4client import Cards, openingHeros, Coin
from gameModules.Player import *
# from gameModules.Spells import Coin
# from Minions import *
# from Weapon import *
import os, time
import my_collections as coll


class PublicBattle:
    # 双方共享的战场信息
    def __init__(self):
        self.tiggerField = []
        self.allminions = []  # 所有随从,用于按顺序结算


recvMsgs = []


def log(*msg):
    print(*msg)


class Battle(cocos.layer.ColorLayer):
    is_event_handler = True

    def __init__(self):
        super().__init__(162, 205, 90, 255)
        self.cnum = 4  # TODO delete
        self.status = 'ready'
        self.debug = True
        self.initImage()

    def assistDebug(self):  # TODO delete
        self.me.modCrystal(10, 10)
        self.connect.send(('debug', [self.cnum]))
        time.sleep(1)
        act, local.args = recvMsgs.pop(0)
        self.me.drawCard(self.cnum)

    # 匹配
    def match(self):
        self.connect = Connect()
        self.connect.connect(local.id, local.curDeckID)
        data = self.connect.recv()
        if data == None:
            return logger.error('匹配超时')
        self.cardlist = []  #待选
        self.selected = []  #选中
        self.commitArgs = []  #暂存变量
        self.status = 'beforeBattle'
        self.renderOpening(data)  # 绘制开场信息并等待换牌

    #卡牌选择或替换
    def renderBigCards(self, cards):
        #双方战场绘制区域初始化
        x, y = self.center
        num = len(cards)
        w, h = local.winWidth, local.winHeight
        posx0 = x - (0.3 * w)  # 第一张牌的位置
        distance = 0.6 * w / (num - 1)  # 相邻两张牌的距离
        for card in cards:
            logger.debug(card.name)
            card.initImage()
            # 将其加入场景
            local.battleScene.add(card)
            i = cards.index(card)
            card.do(
                MoveTo((posx0 + distance * i, y + h / 10), 1.5) +
                ScaleBy(2, 0.5))
        self.cardlist = cards
        # 确定按钮
        self.add(self.confirmBtn, z=3)

    #开场
    def renderOpening(self, data):
        # 对方昵称，对方英雄，己方英雄，起始手牌
        opNickName, myHeroID, opHeroID, self.cardlist = data  #获取开场信息、起始手牌
        # print(data)
        # 公共战场信息
        local.battle = PublicBattle()
        me = self.me = Player(openingHeros[myHeroID](), isOpponent=False)
        me.opponent = Player(openingHeros[opHeroID](), isOpponent=True)
        # 我对手的对手是我
        me.opponent.opponent = me
        # 昵称
        enemyNickName = opNickName
        myNickName = local.nickName
        # 绘制待替换卡牌
        self.selected = []  # 换牌时selected比较特殊，是个list
        self.renderBigCards(self.cardlist)

    #起手换牌
    def replace(self):
        newCards = self.connect.send_recv(self.selected)
        logger.debug('换来的牌%s', newCards)
        cards = self.cardlist
        #重新安排cards
        for i in self.selected:
            cards[i] = newCards.pop(0)
            cards[i].initImage()
            # 将其加入场景
            local.battleScene.add(cards[i])
        if len(cards) == 4:
            #硬币入手
            coin = Coin()
            cards.append(coin)
            local.battleScene.add(coin)
        #将开场卡牌加入手牌
        for card in cards:
            card.getDrawed(self.me)
            # card.holder = self.me
        # self.me.hand = cards
        self.me.renderHand()
        self.me.opponent.drawCard(5 if len(cards) == 3 else 3)
        #重置cardlist和selected
        self.cardlist = []
        self.selected = None
        #另起线程监听服务端order
        _thread.start_new_thread(self.listenOrder, ())
        #若先手，则置为我的回合
        if len(cards) == 3:
            self.status = 'myTurnReady'
        else:
            self.status = 'enemyTurn'
            # 设置玩家回合
            self.me.opponent.myTurn = True

    # 回合开始
    def myTurnStart(self):
        logger.info('回合开始')
        #回合开始
        while not recvMsgs:
            time.sleep(0.1)
        # 设置玩家回合
        self.me.myTurn = True
        self.me.opponent.myTurn = False
        # 处理命令和参数
        order, local.args = recvMsgs.pop(0)
        self.me.genEvent(order, self.me)
        self.me.clear()
        if self.debug:
            self.assistDebug()
            self.debug = False
        self.cardlist = self.me.getAvailables()
        # 显示回合结束按钮
        self.add(self.endTurnBtn)

    # 对手行动
    def enemyAction(self):
        if not recvMsgs:
            return
        print('enemyAction', recvMsgs)
        order, local.args = recvMsgs.pop(0)
        # print('local args  ss', local.args)
        player = self.me.opponent
        if isinstance(order, Event):
            self.me.genEvent(order, player)
            if order == Event.回合结束:
                self.status = 'myTurn'
                self.myTurnStart()
                # break
        elif order == 'play':
            # args = local.args[0]
            # handIdx = args[0]
            player.play()
        elif order == 'attack':
            args = local.args.pop(0)
            card = fromLocation(args[0], player)
            target = fromLocation(args[1], player)
            card.attacking(target)
        elif order == 'power':
            pass
        elif order == 'debug':
            self.me.opponent.modCrystal(10, 10)
            self.me.opponent.drawCard(self.cnum)
        self.me.clear()

    # 监听通知
    def listenOrder(self):
        while True:
            order = self.connect.recv(1024)
            recvMsgs.append(order)
            log(('listen', recvMsgs))
            _thread.start_new_thread(self.mousemove, ())

    def commitOrder(self, act):
        card = self.selected
        log(card)
        self.connect.send((act, self.commitArgs))
        while not recvMsgs:
            time.sleep(0.2)
        order, local.args = recvMsgs.pop(0)
        if act == 'play':
            # 随从：handIdx, minionIdx, [targetLoc]
            # 其他：handIdx, [targetLoc]
            handIdx = self.commitArgs.pop(0)  #TODO 待测
            self.me.hand[handIdx].play(*self.commitArgs)
        elif act == 'attack':
            log(self.commitArgs)
            fromLocation(self.commitArgs[0], self.me).attacking(
                fromLocation(self.commitArgs[1], self.me))
        elif act == 'turnEnd':
            self.me.genEvent(Event.回合结束)
            # 设置玩家回合
            self.me.myTurn = False
            self.me.opponent.myTurn = True
            self.status = 'enemyTurn'
            self.fade()
            self.remove(self.endTurnBtn)
        self.me.clear()

    def mousemove(self):
        while True:
            if local.animingMutex == 0:
                curx, cury = simuInput.getPos()
                if self.status == 'enemyTurn' and recvMsgs:
                    simuInput.moveTo(local.winWidth - 6, local.winHeight - 6)
                elif self.status == 'myTurnReady':
                    simuInput.moveTo(local.winWidth - 6, local.winHeight - 3)
                #功成身退，回到原位
                # time.sleep(0.05)
                # print(self.status)
                # simuInput.moveTo(curx, cury)
                return
            else:
                time.sleep(0.1)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.status == 'enemyTurn' and recvMsgs:
            self.enemyAction()
        elif self.status == 'myTurnReady' and x >= local.winWidth - 6 and y >= local.winHeight - 6:
            self.status = 'myTurn'
            self.myTurnStart()

    def on_mouse_press(self, posx, posy, buttons, modifiers):
        if self.status == 'myTurn' and self.me.myTurn:
            card = self.clickCard(self.cardlist, posx, posy)
            if card:
                logger.warning('箭头')
                self.add(self.arrow, z=4)
                self.status = 'arrow'
                self.selected = card
                self.fade()
                card.do(ScaleBy(1.5, 0))
            if self.hitIt(posx, posy, self.endTurnBtn, self):
                # 回合结束
                logger.info('回合结束按钮')
                self.commitOrder('turnEnd')
        elif self.status == 'battlecry':
            target = self.clickCard(self.cardlist, posx, posy)
            if target:
                # getLocation(target)
                self.commitArgs.append(toLocation(target))
                self.commitOrder('play')
        elif self.status == 'enemyTurn':
            self.enemyAction()
        elif self.status == 'beforeBattle':
            ##换牌
            card = self.clickCard(self.cardlist, posx, posy)
            if card:
                idx = self.cardlist.index(card)
                #此时比较特殊，selected存放的是序号
                if idx in self.selected:
                    card.remove(card.cross)
                    self.selected.remove(idx)
                else:
                    card.cross = Sprite(local.res['cross'],
                                        position=card.items['frame'].position,
                                        scale=local.itemScale * card.scale * 4)
                    card.add(card.cross, z=3)
                    self.selected.append(idx)
                return
            if self.hitIt(posx, posy, self.confirmBtn, self):
                # self.status = 'myTurnReady'
                for idx in self.selected:
                    local.battleScene.remove(self.cardlist[idx])
                self.remove(self.confirmBtn)
                self.replace()

    #判断指定对象是否被点击
    def hitIt(self, posx, posy, sprite, node):
        nodex, nodey = node.position
        spritex, spritey = sprite.position
        x, y = spritex + nodex, spritey + nodey
        w, h = sprite.width * node.scale, sprite.height * node.scale
        if x - w / 2 < posx < x + w / 2 and y - h / 2 < posy < y + h / 2:
            return True

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.status == 'arrow':
            #箭头跟随鼠标
            self.arrow.position = x, y

    def on_mouse_release(self, posx, posy, buttons, modifiers):
        if self.status != 'arrow':
            return
        #箭头消失
        self.remove(self.arrow)
        self.status = 'none'
        #当前操纵卡牌
        card = self.selected
        me = self.me
        # 若为手牌，将其位置作为提交的第一个参数
        if card in self.me.hand:
            self.commitArgs = [self.me.hand.index(card)]
        # 随从牌
        if card in self.me.hand and card.type == 'minion':
            x, y, w, h = me.minionRegion
            if x < posx < x + w and y < posy < y + h:
                fieldIdx = 0
                for m in me.minionField:
                    if m.position[0] < posx:
                        fieldIdx += 1
                    else:
                        break
                self.commitArgs.append(fieldIdx)
                # 若有战吼目标
                # 或有连击、有连击计数且有连击目标
                # 直接返回，保留self.selected
                if card.targetType and (
                    ('combo' not in card.exts) or
                    ('combo' in card.exts and card.holder.comboCount > 0)):
                    logger.info('战吼或连击')
                    self.cardlist = card.getSelectables()
                    if self.cardlist:
                        self.status == 'battlecry'
                        return
                    #若没有符合条件的战吼目标，取消战吼直接登场
                # print(card.name, '直接登场')
                self.commitOrder('play')
        #无需指定目标的手牌
        elif posy < me.minionRegion[1]: # 需上移一定距离才可打出，防误触
            pass
        elif card in self.me.hand and not card.targetType:
            self.commitOrder('play')
        else:
            print('法术',me.minionRegion[1],posy)
            #获得所有可针对的目标
            targets = card.getSelectables()
            #获取当前位置且可针对的目标
            target = self.clickCard(targets, posx, posy)
            #没有满足条件的目标
            if not target:
                return
            #若卡牌为场上角色，发起攻击
            if card in card.holder.minionField + [self.me.hero]:
                self.commitArgs = [
                    toLocation(card, me),
                    toLocation(target, me)
                ]
                self.commitOrder('attack')
            else:
                self.commitArgs.append(self.getLocation(target))
                self.commitOrder('play')
        self.settle()

    #整理场面
    def settle(self):
        self.status = 'myTurn'
        self.arrow.position = (-100, -100)
        self.fade()
        self.cardlist = self.me.getAvailables()
        self.selected.scale = local.cardScale
        self.selected = None
        self.commitArgs = []
        self.me.renderHand()
        if not self.cardlist:
            #没有可做的事了
            #TODO 特殊提示
            pass

    # 键盘按压
    def on_key_press(self, key, modifiers):
        if self.status == 'ready' and key == local.keyCode['space']:
            self.status = ''
            logger.info('匹配中')
            self.match()

    #消除可选/可操作光圈
    def fade(self):
        log(self.cardlist)
        for card in self.cardlist:
            try:
                card.remove(card.items['circle'])
            except:
                logger.debug('%s没有光圈', card.name)

    #若有卡牌在点击范围，返回这张卡
    def clickCard(self, cards, posx, posy):
        for card in cards:
            # x,y=card.position
            # print(x,y)
            # w,h = card.items['frame'].width*card.scale, card.items['frame'].height*card.scale
            # if x-w/2<posx<x+w/2 and y-h/2<posy<y+h/2:
            if self.hitIt(posx, posy, card.items['frame'], card):
                return card
        return None

    #绘制战场按钮
    def initImage(self):
        self.center = (director.get_window_size()[0] / 2,
                       director.get_window_size()[1] / 2)
        posx, posy = self.center
        # 棋盘
        self.chessboard = Sprite(local.res['chessboard'],
                                 position=self.center,
                                 scale=local.winHeight * 0.8 / 1000)
        self.add(self.chessboard)
        # 确认按钮
        self.confirmBtn = Sprite(local.res['confirm'],
                                 position=(posx, posy - 0.2 * local.winHeight),
                                 scale=local.winHeight * 0.6 / 1000)
        # 红箭头
        self.arrow = Sprite(local.res['arrow'], position=(-100, -100))
        # 回合结束按钮
        self.endTurnBtn = Sprite(local.res['end_turn'],
                                 position=local.endTurnPos)
        #初始化模拟点击
        simuInput.init(local.director)
        _thread.start_new_thread(simuInput.key_press, ('space', ))


class SelectLayer(cocos.layer.ColorLayer):
    is_event_handler = True

    def __init__(self):
        super().__init__(162, 205, 90, 255)
        self.center = (director.get_window_size()[0] / 2,
                       director.get_window_size()[1] / 2)
        self.bg = Sprite('resource/select.png',
                         position=self.center,
                         scale=local.winHeight * 0.0007)
        self.add(self.bg)
        self.bg.do(ScaleBy(0.9, duration=0.5))
        # 套牌封面位置九宫格
        posxs = [0.202, 0.35, 0.5]
        posys = [0.73, 0.5, 0.20]
        self.decks = []
        for i in range(len(local.myDecks)):
            deckname = Label(local.myDecks[i]['name'],
                             bold=True,
                             font_name='Microsoft Yahei',
                             font_size=60 * local.cardScale,
                             anchor_x='center',
                             anchor_y='center',
                             dpi=300)
            deckcover = Sprite(local.res[f'logo{local.myDecks[i]["hero"]}'])
            deckcover.position = deckname.position = local.winWidth * posxs[
                i % 3], local.winHeight * posys[i // 3]
            self.decks.append([deckcover, deckname])
            self.add(deckcover)
            self.add(deckname)

    def on_mouse_press(self, posx, posy, buttons, modifiers):
        for deck in self.decks:
            x, y = deck[0].position
            w, h = deck[0].width, deck[0].height
            if x - w / 2 < posx < x + w / 2 and y - h / 2 < posy < y + h / 2:
                local.curDeckID = self.decks.index(deck)
                battle = Battle()
                battleScene = scene.Scene(battle)
                local.battleScene = battleScene
                local.director.run(battleScene)
        x1, y1 = 0.24, 0.06
        x2, y2 = 0.41, 0.10
        w, h = self.bg.width, self.bg.height
        if w * x1 < posx < w * x2 and h * y1 < posy < w * y2:
            if not coll.coll:
                coll.coll = coll.Collections()
            collScene = scene.Scene(coll.coll)
            local.director.run(collScene)

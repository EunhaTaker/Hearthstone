from configs.common import logger
from tools import *
from gameModules.Interface import *
# from Minions import *
# from Spell import *
# from Hero import *
# from Weapon import *
from gameModules.Player import Player
# 全卡牌列表，按职业分
from gameModules.Cards4server import Cards, openingHeros, Coin

professions = [Druid, Hunter, Mage, Paladin, Priest,
               Rogue, Shaman, Warlock, Warrior, Neutral]
for p in professions:
    ts = list(set(p.__subclasses__()).difference(set(Derive.__subclasses__())))
    ts.sort(key=lambda x: x.cost)
    Cards.append(ts)
logger.debug('卡牌',Cards)

class PublicBattle:
    # 双方共享的战场信息
    def __init__(self):
        self.tiggerField = []
        self.allminions = []  # 所有随从,用于按顺序结算


from threading import *
from gameModules.Interface import Event #截胡
import time
import _thread
#对战
class BattleThread(Thread):
    def __init__(self, info1, info2):
        Thread.__init__(self)
        self.c1 = {}
        self.c2 = {}
        clients = self.c1, self.c2
        infos = info1, info2
        # 公共战场信息
        self.battle = PublicBattle()
        # 初始化双方数据
        for p, info in zip(clients, infos):
            p['conn'],p['nickName'] = info[0], info[3]
            deck = json.loads(info[2])
            #英雄id
            p['heroID'] = deck['hero']
            # 实例化英雄及玩家
            p['player'] = Player(self.battle, openingHeros[p['heroID']]())
            deckCards = deck['cards']
            deck = p['player'].deck
            #套牌初始化
            for i in range(len(deckCards)):
                m,n = deckCards[i]
                logger.debug(Cards[m][n])
                deckCards[i] = Cards[m][n]()
            deck.range(deckCards)
            logger.debug('起始套牌%s',deck)
            # 分配起始手牌
            ncards = 3+clients.index(p)
            p['openingHand'] = deck.open(ncards)
        #传递起始信息并等待玩家替牌
        self.confirmed = 0  # 替牌完成数
        for p in clients:
            msg = (clients[clients.index(p)-1]['nickName'], p['heroID'],
                   clients[clients.index(p)-1]['heroID'], p['openingHand'])
            send(p['conn'], msg)
            logger.warning('开场内容%s',msg)
            #为双方各起一个线程用于换牌
            _thread.start_new_thread(self.replace, (p,))

    def run(self):
        while True:
            time.sleep(1)
            if self.confirmed == 2:
                self.c1['player'].opponent = self.c2['player']
                self.c2['player'].opponent = self.c1['player']
                break
        #对战主循环
        while True:
            #双方玩家的循环
            for c, oc in zip((self.c1,self.c2), (self.c2,self.c1)):
                player = c['player']
                opponentPlayer = oc['player']
                # 回合开始
                player.myTurn = True
                player.genEvent(Event.回合开始, player)
                self.sendOrder(Event.回合开始)
                player.clear()
                # 一回合的循环
                while True:
                    # 接收行动
                    act, args = recv(c['conn'])
                    logger.info((act, args))
                    # 将行动参数添加到对手args
                    opponentPlayer.args = [args[:]]
                    if act == 'play':
                        handIdx = args.pop(0)
                        player.log()
                        player.hand[handIdx].play(*args)
                    elif act == 'attack':
                        card = fromLocation(args[0], player)
                        target = fromLocation(args[1], player)
                        card.attacking(target)
                    elif act == 'power':
                        pass
                    elif act == 'turnEnd':
                        player.genEvent(Event.回合结束, player)
                        self.sendOrder(Event.回合结束)
                        player.myTurn = False
                        time.sleep(player.sleeptime+opponentPlayer.sleeptime+1)
                        act = Event.回合结束
                        break
                    elif act == "debug":
                        player.drawCard(args[0])
                    player.clear()
                    self.sendOrder(act)

    def sendOrder(self, order):
        ## 发送必要信息给双方客户端
        for client in self.c1, self.c2:
            send(client['conn'], (order, client['player'].args))
            client['player'].args = []
            client['player'].sleeptime = 0

    def replace(self, p):
        ## 接受玩家起手换牌
        replaces = recv(p['conn'])
        # logger.debug("数量",replaces)
        deck = p['player'].deck
        logger.warn('套牌替换，剩余卡牌：%s',deck)
        #换牌
        openings = p['openingHand']
        newCards = deck.replace(openings, replaces)
        # 若p为后手，额外分配一个硬币
        if p == self.c2:
            openings.append(Coin())
        #发给客户端
        send(p['conn'], newCards)
        # 调用起始手牌的getDrawed
        for card in openings:
            card.getDrawed(p['player'])
        #确认者数+1
        self.confirmed += 1

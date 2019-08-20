# from Connect import Connect
# from Minions import *
# from Spell import *
# from Hero import *

##配置信息
#导演（窗口）
director = None
windowSize = (2400, 1600)
winWidth, winHeight = windowSize
keyCode = {
    'r':114,
    'space':32,
}
#卡牌描述每行最大字数
descLen1Line = 10
#我方水晶绘制区
myCrystalRegion = (winWidth, winHeight*0.05, -winWidth*0.05, winHeight*0.35)
#敌方水晶绘制区
enemyCrystalRegion = (winWidth, winHeight*0.95, -winWidth*0.05, -winHeight*0.35)
# 结束回合按钮中心点
endTurnPos = (winWidth*0.95, winHeight*0.55)
#卡牌组件缩放比例
itemScale = 5*winHeight/4000
#卡牌整体缩放比例
cardScale = 0.2
#手牌上限
handCeiling = 10
#随从上限
minionCeiling = 7
#水晶上限
MaxCrystal = 10
#卡牌宽度
cardWidth = 482*cardScale*itemScale
#卡牌高度
cardHeight = 666*cardScale*itemScale
#手牌间隙
# cardInterval = cardWidth*0.2
# #随从间隙
# minionInterval = cardWidth*0.4
# 我方手牌绘制区
myHandRegion = winWidth*0.2, 0, winWidth*0.65, cardHeight*1.2
# 敌方方手牌绘制区
enemyHandRegion = 0, winHeight, winWidth*0.65, -cardHeight*1.2
# 我方随从绘制区
myMinionRegion = winWidth*0.14, winHeight*0.34, winWidth*0.72, winHeight*0.18
# 敌方随从绘制区
enemyMinionRegion = winWidth*0.14, winHeight*0.54, winWidth*0.72, winHeight*0.18

#卡牌类
Cards = []
openingHeros = None

##个人信息
id = None
nickName = ''
myDecks = []


##战斗信息
battle = None
curDeckID = None
curHero = None
# connect = None
battleScene = None
# 触发器场，双方玩家共享
tiggerField = []
# 按召唤顺序储存所有随从
allminions = []
args = None
#播放动画中
animingMutex = 0


#资源缓存
import os
resPath = os.path.join(os.path.dirname(os.path.dirname(__file__)), r'resource')
res = {}



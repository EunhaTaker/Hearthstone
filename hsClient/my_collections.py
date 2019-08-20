from gameModules.Interface import *
from user import *
from gameModules.Cards4client import Cards
# from Minions import *
# from Spell import *
# from Hero import *
# from Weapon import *
# Cards = [
#     [Acornbearer,], #德
#     [], #猎
#     [], #法
#     [MurlocKnight,], #骑
#     [NorthShireCleric,Chameleos,], #牧
#     [EdwinVanCleef,], #贼
#     [], #萨
#     [Howlfiend], #术
#     [KoblodBarbarian,], #战
#     [GrimPatron,MecHaroo,IronbeakOwl,Pig], #中
# ]
# import cocos
# sprite = cocos.sprite
# Label = cocos.text.Label

class Collections(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self):
        super().__init__()
        professions = [Druid, Hunter, Mage, Paladin, Priest,
                       Rogue, Shaman, Warlock, Warrior, Neutral]
        # # 全卡牌列表，按职业分
        # self.cards = []
        # for p in professions:
        #     ts = list(set(p.__subclasses__()).difference(set(Derive.__subclasses__())))
        #     ts.sort(key= lambda x: x.cost)
        #     self.cards.append(ts)
        # print('卡牌',self.cards)
        # 页码
        self.npage = 0
        # 每页显示卡牌数
        self.npp = 8
        # 当前职业
        self.npfs = 0
        # 筛选条件
        self.filter = ''
        # 当前卡牌列表
        self.cardlists = Cards
        # 创建套牌中
        self.creating = False
        ## 素材
        self.board = Sprite(local.res['collection_board'])
        # 背景板宽高
        self.bwidth, self.bheight = self.board.width, self.board.height
        self.board.position = self.bwidth/2, self.bheight/2
        # 可显职业列表、显示卡牌列表
        self.ps = list(range(10))
        self.showlist = []
        # 卡牌位置
        self.hposes = [0.72*self.bheight, 0.33*self.bheight]
        self.wposes = [0.16*self.bwidth, 0.38 *
                       self.bwidth, 0.6*self.bwidth, 0.82*self.bwidth]
        # 图标、水印，TODO尺寸待适配
        self.icons = []
        self.stamps = []
        self.iwidth, self.iheight = 90*1.3, 70
        self.stampWidth, self.stampHeight = self.board.width*0.49, self.board.height*0.885
        for i in range(10):
            icon = Sprite(local.res['collicon'+str(i)])
            icon.position = self.iwidth*(i+0.5), self.bheight+self.iheight/2
            self.icons.append(icon)
            stamp = Sprite(local.res['stamp'+str(i)])
            stamp.position = self.stampWidth, self.stampHeight+stamp.height/2
            self.stamps.append(stamp)
        # 套牌列表背景板
        self.decksBoard = Sprite(local.res['decks_board'])
        self.decksBoard.position = local.winWidth-self.decksBoard.width/2, local.winHeight-self.decksBoard.height/2
        # 套牌编辑背景
        self.editBg = Sprite(local.res['deck_bg'])
        self.editBg.position = self.decksBoard.position
        # 我的套牌
        self.decks = []
        # self.deckWidth, self.deckHeight = local.res['create_deck'].width*1.2,local.res['create_deck'].height*1.4
        ## 创建套牌按钮
        createBtn = Sprite(local.res['create_deck'])
        x,y = self.decksBoard.position
        createBtn.position = x-self.decksBoard.width*0.06, y+self.decksBoard.height*0.35
        self.decks.append(createBtn)
        self.createBtn = createBtn
        for deck in local.myDecks:
            self.addDeck(deck)
        # 套牌编辑
        ## 第一张卡（或创建按钮）位置，便于后续计算
        if len(self.decks)==1:
            self.editPos0 = self.decks[0].position
        else:
            self.editPos0 = self.decks[0][1].position
        ## 编辑区卡牌高度
        self.editHeight = local.cardScale*200
        ## 用于储存编辑区卡牌label
        self.cardSprs = []
        # 完成编辑按钮
        self.doneBtn = Sprite(local.res['done'])
        self.doneBtn.position = local.winWidth-self.doneBtn.width/2,\
                                    local.winHeight-self.decksBoard.height
        self.setBtnClick()
        # 绘制
        self.initImage()

    # 添加按钮点击效果
    def setBtnClick(self):
        self.buttons = [self.createBtn, self.doneBtn]
        # 创建新套牌
        def create(npfs=-1):
            if npfs == -1:
                import random
                npfs = random.randint(0, 8)
            self.setProfession(npfs=npfs)
            self.newDeck = True
            self.cardlists = [Cards[i] if i in [npfs, 9] else []
                              for i in range(10)]
            pnames = ['德鲁伊', '猎人', '法师', '骑士', '牧师', '潜行者', '萨满', '术士', '战士']
            self.curdeck = {}
            self.curdeck['name'] = '自定义'+pnames[npfs]
            self.curdeck['hero'] = npfs
            self.curdeck['cards'] = []
            self.initDeckview()
        self.createBtn.click = create
        # 编辑完毕
        def editDone():
            if self.newDeck:
                User.createDeck(self.curdeck)
                local.myDecks.append(self.curdeck)
                self.addDeck(self.curdeck)
                self.add(self.decks[-2][0], z=0.1)
                self.add(self.decks[-2][1], z=0.2)
                self.cardlists = Cards
            else:
                User.updateDeck(self.curdeck, local.myDecks.index(self.curdeck))
            self.creating = False
            self.remove(self.editBg)
            self.remove(self.doneBtn)
            for spr in self.cardSprs:
                self.remove(spr)
            self.cardSprs = []
        self.doneBtn.click = editDone

    def addDeck(self, deck):
        deckname = Label(deck['name'], bold=True,
                         font_name='Microsoft Yahei', font_size=60*local.cardScale,
                         anchor_x='center', anchor_y='baseline', dpi=300)
        deckname.position = self.decks[-1].position
        deckcover = Sprite(local.res[f'logo{deck["hero"]}'])
        deckcover.position = self.decks[-1].position
        self.decks.insert(-1, [deckcover, deckname])
        self.createBtn.position = self.createBtn.position[0], self.createBtn.position[1] - \
            self.createBtn.height*1.4   #self.deckHeight

    def initImage(self):
        self.add(self.board, z=0.1)
        for icon in self.icons:
            self.add(icon)
        self.icons[self.npfs].scale = 1.5
        self.add(self.stamps[self.npfs], z=0.2)

        self.add(self.decksBoard)
        for deck in self.decks[:-1]:
            self.add(deck[0], z=0.1)
            self.add(deck[1], z=0.2)
        self.add(self.decks[-1])

        self.broswer()

    # 显示套牌编辑界面
    def initDeckview(self):
        self.creating = True
        self.add(self.editBg, z=1)
        self.add(self.doneBtn, z=1.2)
        cards = self.curdeck['cards']
        for card in cards:
            name = Cards[card[0]][card[1]].name
            cardLabel = Label(name, bold=True,
                          font_name='Microsoft Yahei', font_size=25*local.cardScale,
                          anchor_x='center', anchor_y='baseline', dpi=300)
            try:
                x,y = self.cardSprs[-1].position
                cardLabel.position = x, y-self.editHeight
            except:
                cardLabel.position = self.editPos0
            self.add(cardLabel, z=1.1)
            self.cardSprs.append(cardLabel)

    def on_mouse_release(self, posx, posy, buttons, modifiers):
        # print((posx-self.decksBoard.position[0])/self.decksBoard.width,
            #   (posy-self.decksBoard.position[1])/self.decksBoard.height)
        if 0.01*self.bwidth < posx < 0.06*self.bwidth and \
            0.097*self.bheight < posy < 0.97*self.bheight:
            # 左翻页区
            if self.npage == 0:
                self.setProfession(opt='preview')
            else:
                self.npage -= 1
                self.broswer()
        elif 0.91*self.bwidth < posx < 0.956*self.bwidth \
            and 0.097*self.bheight < posy < 0.97*self.bheight:
            # 右翻页区
            if self.npage >= (len(self.cardlists[self.npfs])+self.npp-1)//self.npp-1:
                self.setProfession(opt='next')
            else:
                self.npage += 1
                self.broswer()
        elif self.bheight < posy < self.bheight+self.iheight:
            halfw = self.iwidth/2
            # 职业图标区
            for p in self.ps:
                px = self.icons[p].position[0]
                if px-halfw < posx < px+halfw:
                    if self.npfs != p:
                        self.setProfession(npfs=p)
                    break
        else:
            for btn in self.buttons:
                # 按钮
                if self.hitIt(posx, posy, btn):
                    btn.click()
                    return
            print(self.showlist)
            for card in self.showlist:
                # 卡牌展示区
                if self.hitIt(posx, posy, card.items['frame'], card):
                    if self.creating:
                        print('hit',card)
                        site = (self.npfs, Cards[self.npfs].index(type(card)))
                        if self.curdeck['cards'].count(site) >= (1 if card.rarity=='legendary' else 2):
                            return print('超出数量限制')
                        self.curdeck['cards'].append(site)
                        cardLabel = Label(card.name, bold=True,
                                          font_name='Microsoft Yahei', font_size=25*local.cardScale,
                                          anchor_x='center', anchor_y='baseline', dpi=300)
                        if self.cardSprs:
                            x, y = self.cardSprs[-1].position
                            cardLabel.position = x, y-self.editHeight
                        else:
                            cardLabel.position = self.editPos0
                        self.add(cardLabel,z=1.1)
                        self.cardSprs.append(cardLabel)
                    return
            for deck in self.decks[:-1]:
                # 套牌列表区
                if self.hitIt(posx, posy, deck[0]):
                    # 编辑原有套牌
                    self.newDeck = False
                    self.curdeck = local.myDecks[self.decks.index(deck)]
                    self.initDeckview()

    def hitIt(self, posx, posy, spr, node=None):
        w, h = spr.width/2, spr.height/2
        x, y = spr.position
        if node:
            w *= local.itemScale*local.cardScale
            h *= local.itemScale*local.cardScale
            x0, y0 = node.position
            x += x0
            y += y0
        if x-w < posx < x+w and y-h < posy < y+h:
            return True
            
    def broswer(self):
        for card in self.showlist:
            self.remove(card)
        cardlist = self.cardlists[self.npfs]
        self.showlist = cardlist[self.npage*self.npp:
                        min((self.npage+1)*self.npp, len(cardlist))]
        print('browser',self.showlist)
        for i in range(len(self.showlist)):
            card = self.showlist[i]()
            self.add(card, z=1)
            card.scale *= 1.8
            card.position = self.wposes[i%4], self.hposes[i//4]
            self.showlist[i] = card

    def setFilter(self, filter=None):
        idx = 0
        self.npfs = -1
        for i in range(10):
            if self.cardlist[i]:
                self.npfs = i
                if i not in self.ps:
                    ps.insert(idx, i)
                    self.add(self.icons[i])
                self.icons[i].position = self.iwidth * \
                    (idx+0.5), self.bheight+self.iheight/2
                idx += 1
            elif i in self.ps:
                self.ps.remove(i)
                self.remove(self.icons[i])
        if idx == 0:
            # TODO没有符合条件的卡牌
            pass
        else:
            self.npfs = ps[0]
        self.npage = 0

    def setProfession(self, npfs=None, opt=''):
        idx = self.ps.index(self.npfs)
        if opt=='preview':
            if idx>0:
                npfs = self.ps[idx-1]
                self.npage = (
                    len(self.cardlists[self.npfs])+self.npp-1)//self.npp
            else:
                return
        elif opt=='next':
            if  idx < len(self.ps)-1:
                npfs = self.ps[idx+1]
            else:
                return
        # TODO无牌
        else:
            npfs = npfs or 0
        self.icons[self.npfs].scale = 1
        self.remove(self.stamps[self.npfs])
        self.npfs = npfs
        self.icons[npfs].scale = 1.5
        self.add(self.stamps[npfs], z=0.2)
        self.broswer()

coll = None

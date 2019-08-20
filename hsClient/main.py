from configs.common import logger
import os
import user as user
from Battle import *
import gameModules.local as local
import cocos
import pyglet
from cocos.actions import *
director = cocos.director.director
sprite = cocos.sprite
scene = cocos.scene
# import pyautogui as gui

#加载资源
def loadResource():

    for items in ['other_items', 'items', 'hero_items', 'minion_items', 'spell_items', 'weapon_items', 'icon_items']:
        for imgName in os.listdir(os.path.join(local.resPath, items)):
            logger.debug('加载图片:%s',imgName)
            imgPath = os.path.join(local.resPath, items, imgName)
            local.res[imgName.replace('.png', '')] = pyglet.image.load(
                imgPath)
    logger.info('加载完毕')

# from Minions import *
class MenuLayer(cocos.layer.ColorLayer):
    is_event_handler = True

    def __init__(self):
        super().__init__(162,205,90,100)
        self.center = (director.get_window_size()[
                    0] / 2, director.get_window_size()[1] / 2)
        self.mainBG = sprite.Sprite(
            'resource/main.png', position=self.center, scale=local.winHeight/800)
        self.add(self.mainBG, z=0)
        self.mainBG.do(ScaleBy(0.8, duration=2))


    def on_mouse_press(self, posx, posy, buttons, modifiers):
        if not test:
            # 进入套牌选择界面
            select = SelectLayer()
            selectScene = scene.Scene(select)
            director.run(selectScene)
        else:
            self.add(self.mainBG)
            print(self.get_children())
            
            # gui.press('f4',interval=0.5)
            # gui.press('space',interval=0.5)
        # m = MurlocKnight()
        # m.position = (300, 300)
        # mainScene.add(m)
        
    def on_key_press(self, key, modifiers):
        print(key, modifiers)


    # def on_mouse_motion(self, x, y, dx, dy):
    #     # print('drag',x,y)
    #     global t
    #     t1=time.time()
    #     print(t1-t)
    #     t=t1

    # def on_mouse_release(self, posx, posy, buttons, modifiers):
    #     print('rele')

def autoLogin():
    user.User.login('780', '111')
    # user.User.register('780', '111')
    # c.createDeck('测试套牌2', 0, [(0,0),(0, 1), (0, 2)])

test = 0
if __name__ == '__main__':
    
    if not test:
        autoLogin()
        if local.id:
            import _thread
            #丢进线程预先加载
            _thread.start_new_thread(loadResource,())
    director.init(width=local.winWidth, height=local.winHeight)
    # director.set_show_FPS(True)
    local.director = director
    menu = MenuLayer()
    mainScene = scene.Scene(menu)
    director.run(mainScene)
        

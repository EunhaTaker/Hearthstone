import pyautogui as gui
import gameModules.local as local
import time

getLoc = None
winWidth = 0
winHeight = 0

def init(director):
    global getLoc, winHeight, winWidth
    getLoc = director.window.get_location
    winWidth, winHeight = director.get_window_size()

def screen_shot(region=None):
    '''截屏'''
    if region:
        img = gui.screenshot(region)
    else:
        img = gui.screenshot()
    img.save('screenshot.png')


def locateOnScreen(imgName):
    '''匹配图片寻找图像位置'''
    region = gui.locateOnScreen(imgName)
    return region

def getPos():
    offx, offy = getLoc()
    rawPosx, rawPosy = gui.position()
    posx = rawPosx - offx
    posy = winHeight - (rawPosy - offy)
    return posx, posy


def transPos(posx, posy):
    offx, offy = getLoc()
    x = offx+posx
    y = offy+winHeight-posy
    return x, y


def mouse_click(posx=None, posy=None, button='left'):
    if posx and posy:
        clickx, clicky = transPos(posx, posy)
        gui.click(clickx, clicky, button=button)
    else:
        gui.click()

def moveTo(posx, posy):
    x, y = transPos(posx, posy)
    gui.moveTo(x, y-1, duration=0)
    time.sleep(0.05)
    gui.moveTo(x, y, duration=0)
    time.sleep(0.05)

def key_press(key):
    gui.press(key)

#注册、登录、创建套牌
import socket
from urllib import request as urlreq
import requests
import json
import time

import gameModules.local as local

class User:

    @staticmethod
    def login(username, password):
        query = f'username={username}&password={password}'
        req = urlreq.Request(f'http://127.0.0.1:5000/login?{query}')
        res = urlreq.urlopen(req).read()
        data = json.loads(res)
        if data:
            local.id = data['id']
            local.nickName = data['nickname']
            myDecks = json.loads(data['decks'])
            for deck in myDecks:
                deck = json.loads(deck)
                local.myDecks.append(deck)
            print('登录成功')
        else:
            print('账号或密码错误')

    @staticmethod
    def register(username, password):
        query = f'username={username}&password={password}'
        req = urlreq.Request(f'http://127.0.0.1:5000/register?{query}')
        res = urlreq.urlopen(req).read()
        if res != 'has exists':
            User.login(username, password)
        else:
            print('账号已存在')
        # User.user = conn.send_recv('register', (username, password))
        # print(User.user)

    @staticmethod
    def createDeck(deck):
        # deck = {}
        # deck['name'] = name
        # deck['hero'] = hero
        # deck['cards'] = cards
        # local.myDecks.append(deck)
        deck = json.dumps(deck)
        data ={
            'id':local.id,
            'deck':deck
        }
        url = 'http://127.0.0.1:5000/createDeck'
        requests.post(url, data=data)

    @staticmethod
    def updateDeck(deck, index):
        deck = json.dumps(deck)
        data = {
            'id': local.id,
            'deck': deck,
            'index': index
        }
        url = 'http://127.0.0.1:5000/updateDeck'
        requests.post(url, data=data)

if __name__=='__main__':
    c = User()
    c.login('222','111')
    # c.createDeck('mydeck', 0, [])


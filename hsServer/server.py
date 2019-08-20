# -*- coding: utf-8 -*-
from battleServer import logger, time, json, pickle, socket
from battleServer import send, send_recv, recv
from battleServer import BattleThread
#数据库连接
import os
import sqlite3
db = sqlite3.connect(f'{os.path.dirname(__file__)}/data/HearthStone.db', check_same_thread=False)
cursor = db.cursor()

#短连接配置
from flask import Flask, request, Response
app = Flask(__name__)

@app.route('/login')
def login():
    username = request.args.get('username','')
    password = request.args.get('password','')
    cursor.execute('select * from user where username=? and password=?',(username,password))
    result = cursor.fetchone()
    calldata={
        'id': result[0],
        'nickname': result[3],
        'decks': result[4]
    } if result else {}
    return json.dumps(calldata)

@app.route('/register')
def register():
    username = request.args.get('username', '')
    password = request.args.get('password', '')
    cursor.execute(
        'select * from user where username=?', (username,))
    exists = cursor.fetchall() != []
    if not exists:
        cursor.execute('insert into user(username, password, decks) values(?,?,?)',(username, password, json.dumps([])))
        db.commit()
    return 'complete' if not exists else 'has exists'

@app.route('/createDeck', methods=['GET', 'POST'])
def createDeck():
    id = int(request.form['id'])
    deck = request.form['deck']
    # print(deck)
    cursor.execute(
        'select * from user where id=?', (id,))
    user = cursor.fetchall()[0]
    decks = json.loads(user[4])
    decks.append(deck)
    strDecks = json.dumps(decks)
    cursor.execute('update user set decks=? where id=?', (strDecks, id))
    db.commit()

    res = Response(response='True', status=200,
                   mimetype='multipart/form-data')
    return res

@app.route('/updateDeck', methods=['GET', 'POST'])
def updateDeck():
    id = int(request.form['id'])
    deck = request.form['deck']
    index = int(request.form['index'])
    cursor.execute(
        'select * from user where id=?', (id,))
    user = cursor.fetchall()[0]
    decks = json.loads(user[4])
    decks[index] = deck
    strDecks = json.dumps(decks)
    cursor.execute('update user set decks=? where id=?', (strDecks, id))
    db.commit()
    res = Response(response='True', status=200,
                   mimetype='multipart/form-data')
    return res

from threading import *
class ClientThread(Thread):  # 提供get/post服务
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        app.run()


#匹配
matchings = []
class matchThread(Thread):  # 用于匹配，只需要生成一个
    def __init__(self):
        Thread.__init__(self)
        
    def run(self):
        while True:
            time.sleep(0.5)
            self.sort()
            if 2 <= len(matchings):
                BattleThread(matchings.pop(0), matchings.pop(0)).start()

    def sort(self):
        for t in matchings[::-1]:
            if t[4]==-1:
                id = t[1]
                cursor.execute(
                    'select * from user where id=?', (id,))
                result = cursor.fetchone()
                #decks, point, nickname
                t[2], t[3], t[4] = json.loads(result[4])[t[2]], result[3], result[5]

#综合服务
class Server:

    def __init__(self):
        self.socket = socket.socket()
        host = socket.gethostname()
        port = 12345
        self.socket.bind((host, port))
        self.socket.listen(5)
        logger.info('监听中')
        # filter = Filter()

        ClientThread().start()  # 登录等服务
        matchThread().start()  # 匹配线程

        while True:
            conn, addr = self.socket.accept()
            logger.debug(addr)
            id, deckID = recv(conn, 128)
            matchings.append([conn, id, deckID, '', -1])
            logger.warning('匹配，数量：%s',len(matchings))


if __name__ == '__main__':
    s = Server()

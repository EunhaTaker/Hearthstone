import socket
import pickle, json



#送收、发送、接收
def send_recv(conn, obj, length=1024):
    msg = pickle.dumps(obj)
    conn.sendall(msg)
    return pickle.loads(conn.recv(length))
def send(conn, obj):
    msg = pickle.dumps(obj)
    conn.sendall(msg)
def recv(conn, length=1024):
    try:
        obj = pickle.loads(conn.recv(length))
        return obj
    except:
        print('ERROR:玩家断开')

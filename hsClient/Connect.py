import socket
import pickle, json

class Connect:

    def connect(self, id, curDeckID):
        self.socket = socket.socket()
        host = socket.gethostname()
        port = 12345
        self.socket.connect((host, port))
        self.send((id, curDeckID))

    def send_recv(self, obj, size=8192):
        msg = pickle.dumps(obj)
        self.socket.sendall(msg)
        return pickle.loads(self.socket.recv(size))

    def send(self, obj):
        msg = pickle.dumps(obj)
        self.socket.sendall(msg)

    def recv(self, size=8192):
        # obj = pickle.loads(self.socket.recv(1024))
        msg = self.socket.recv(size)
        # print('客户端接收：',msg)
        obj = pickle.loads(msg)
        return  obj

if __name__ == '__main__':
    conn = Connect()
    conn.connect(1,0)

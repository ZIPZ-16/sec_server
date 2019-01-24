import threading


class Client(threading.Thread):
    def __init__(self, ip, port, connection):
        threading.Thread.__init__(self)
        self.connection = connection
        self.ip = ip
        self.port = port

    def run(self):

        data = self.connection.recv(1024)
        if data :
            self.connection.sendall(data)
        else :
            self.connection.close()
import socket
import sys
import Client

class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.address = (self.ip, self.port)
        self.server = None
        self.clients = []

    # открытие сокета
    def open_socket(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(self.address)
        except socket.error as e:
            if self.server:
                self.server.close()
            sys.exit(1)

    # обработка запуска сервера
    def run(self):
        self.open_socket()
        self.server.listen(5)

        while True :
            connection, (ip, port) = self.server.accept()

            # каждое подключение заводим новым потоком для определения сессии пользователя
            c = Client.Client(ip, port, connection)
            c.start()

            self.clients.append(c)

        self.server.close()
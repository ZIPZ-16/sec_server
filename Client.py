import json
import threading
import RC5

class Client(threading.Thread):
    def __init__(self, ip, port, connection):
        threading.Thread.__init__(self)
        self.connection = connection
        self.ip = ip
        self.port = port

    def run(self):
        data = self.connection.recv(1024)
        decodedData = RC5.RC5.decryptBytes(data)
        if data :
            jData = json.loads(decodedData)
            if list(jData.keys())[0] == "auth":
                # авторизация
                pass
            elif list(jData.keys())[0] == "postcode":
                # проверка почтового кода
                pass
            elif list(jData.keys())[0] == "getdata":
                # попытка получения информации
                pass
            else:
                # неизвестная команда игнорируется
                pass
            self.connection.sendall(data)
        else :
            self.connection.close()
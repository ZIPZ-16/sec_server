import datetime
import json
import threading
import RC5

class Client(threading.Thread):
    secure_data = {"identfier" : "secure message"}
    logins = {"user1" : "pass1", "user2" : "pass2"}
    wrongs = {}
    bans = {}

    def __init__(self, ip, port, connection):
        threading.Thread.__init__(self)
        self.connection = connection
        self.ip = ip
        self.port = port

    # обработка потока клиента
    def run(self):
        # получение данных от клиента
        data = self.connection.recv(1024)
        # применение расшифровки подключения для получения данных
        decodedData = RC5.RC5.decryptBytes(data)
        if data :
            # получаем информацию от севера в виде JSON
            jData = json.loads(decodedData)

            # выполняем функционал в соответствии с полученным запросом
            if list(jData.keys())[0] == "auth":
                # авторизация
                login = jData["auth"]["login"]
                xorPass = jData["auth"]["pass"]
                # получаем оригинальный хеш пароля
                password = (xorPass.encode() ^ 1100).decode()

                # проверяем на бан
                if login in list(self.bans.keys()):
                    # проверяем актуальность бана и если он уже не актуален чистим базу банов и пускаем
                    delta = datetime.date.today() - self.bans[login]
                    if delta >= 0:
                        del self.bans[login]
                        # сверяем данные, если все верно - пускаем дальше
                        if login in list(self.logins.keys()):
                            if self.logins[login] == "password":
                                # возвращаем ответ-разрешение
                                self.connection.sendall(RC5.RC5.encryptBytes('{"authaccess" : { "status" : "true"}}'))
                                # чистим список ошибочных логинов
                                del self.wrongs[login]
                            else:
                                if login in list(self.wrongs.keys()):
                                    if self.wrongs[login] <= 3:
                                        # меняем счетчик
                                        self.wrongs[login] = self.wrongs[login] + 1
                                    else:
                                        # баним
                                        timestamp = datetime.date.today() + datetime.timedelta(seconds=60)
                                        self.bans.update('{' + login + ' : ' + timestamp + '}')
                                else:
                                    # добавляем счетшик ошибок
                                    self.wrongs.update('{' + login + ' : 1 }')

                                # возвращаем ответ-запрет
                                self.connection.sendall(
                                        RC5.RC5.encryptBytes('{"authaccess" : { "status" : "false"}}'))
                    else:
                        self.connection.sendall(RC5.RC5.encryptBytes('{"authaccess" : { "status" : "ban", "time" : ' + delta + '}}'))
                else:
                    # сверяем данные, если все верно - пускаем дальше
                    if login in list(self.logins.keys()):
                        if self.logins[login] == "password":
                            # возвращаем ответ-разрешение
                            self.connection.sendall(RC5.RC5.encryptBytes('{"authaccess" : { "status" : "true"}}'))
                            # чистим список ошибочных логинов
                            del self.wrongs[login]
                        else:
                            if login in list(self.wrongs.keys()):
                                if self.wrongs[login] <= 3:
                                    # меняем счетчик
                                    self.wrongs[login] = self.wrongs[login] + 1
                                else:
                                    # баним
                                    timestamp = datetime.date.today() + datetime.timedelta(seconds=60)
                                    self.bans.update('{' + login + ' : ' + timestamp + '}')
                            else:
                                # добавляем счетшик ошибок
                                self.wrongs.update('{' + login + ' : 1 }')

                            # возвращаем ответ-запрет
                            self.connection.sendall(
                                RC5.RC5.encryptBytes('{"authaccess" : { "status" : "false"}}'))

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
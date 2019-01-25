import datetime
import json
import random
import smtplib
import threading
import RC5

class Client(threading.Thread):
    secure_data = {"user1" : {"1e7f0fsjs7" : "secure message"}}
    logins = {"user1" : "pass1", "user2" : "pass2"}
    emails = {"user1" : "user1@gmail.com", "user2" : "user2@gmail.com"}
    wrongs = {}
    bans = {}
    postcode = 0
    login = ""
    password = ""

    gmail_user = 'you@gmail.com'
    gmail_password = 'P@ssword!'

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
                self.login = jData["auth"]["login"]
                xorPass = jData["auth"]["pass"]
                # получаем оригинальный хеш пароля
                self.password = (xorPass.encode() ^ 1100).decode()

                # проверяем на бан
                if self.login in list(self.bans.keys()):
                    # проверяем актуальность бана и если он уже не актуален чистим базу банов и пускаем
                    delta = datetime.date.today() - self.bans[self.login]
                    if delta >= 0:
                        del self.bans[self.login]
                        # сверяем данные, если все верно - пускаем дальше
                        if self.login in list(self.logins.keys()):
                            if self.logins[self.login] == "password":
                                # возвращаем ответ-разрешение
                                self.connection.sendall(RC5.RC5.encryptBytes('{"authaccess" : { "status" : "true"}}'))
                                # чистим список ошибочных логинов
                                del self.wrongs[self.login]
                                # отправляем почтовый код
                                self.postcode = random.randrange(99999999)

                                sent_from = self.gmail_user
                                to = self.emails[self.login]
                                subject = 'Сейф'
                                body = "Ваш проверочный код - " + self.postcode

                                email_text = """\  
                                                            From: %s  
                                                            To: %s  
                                                            Subject: %s

                                                            %s
                                                            """ % (sent_from, ", ".join(to), subject, body)
                                try:
                                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                                    server.ehlo()
                                    server.login(self.gmail_user, self.gmail_password)
                                    server.sendmail(sent_from, to, email_text)
                                    server.close()
                                except:
                                    print("Ошибка почты")
                            else:
                                if login in list(self.wrongs.keys()):
                                    if self.wrongs[self.login] <= 3:
                                        # меняем счетчик
                                        self.wrongs[self.login] = self.wrongs[self.login] + 1
                                    else:
                                        # баним
                                        timestamp = datetime.date.today() + datetime.timedelta(seconds=60)
                                        self.bans.update('{' + self.login + ' : ' + timestamp + '}')
                                else:
                                    # добавляем счетшик ошибок
                                    self.wrongs.update('{' + self.login + ' : 1 }')

                                # возвращаем ответ-запрет
                                self.connection.sendall(
                                        RC5.RC5.encryptBytes('{"authaccess" : { "status" : "false"}}'))
                    else:
                        self.connection.sendall(RC5.RC5.encryptBytes('{"authaccess" : { "status" : "ban", "time" : ' + delta + '}}'))
                else:
                    # сверяем данные, если все верно - пускаем дальше
                    if self.login in list(self.logins.keys()):
                        if self.logins[self.login] == "password":
                            # возвращаем ответ-разрешение
                            self.connection.sendall(RC5.RC5.encryptBytes('{"authaccess" : { "status" : "true"}}'))
                            # чистим список ошибочных логинов
                            del self.wrongs[self.login]
                            # отправляем почтовый код
                            self.postcode = random.randrange(99999999)

                            sent_from = self.gmail_user
                            to = self.emails[self.login]
                            subject = 'Сейф'
                            body = "Ваш проверочный код - " + self.postcode

                            email_text = """\  
                            From: %s  
                            To: %s  
                            Subject: %s

                            %s
                            """ % (sent_from, ", ".join(to), subject, body)
                            try:
                                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                                server.ehlo()
                                server.login(self.gmail_user, self.gmail_password)
                                server.sendmail(sent_from, to, email_text)
                                server.close()
                            except:
                                print("Ошибка почты")
                        else:
                            if self.login in list(self.wrongs.keys()):
                                if self.wrongs[self.login] <= 3:
                                    # меняем счетчик
                                    self.wrongs[self.login] = self.wrongs[self.login] + 1
                                else:
                                    # баним
                                    timestamp = datetime.date.today() + datetime.timedelta(seconds=60)
                                    self.bans.update('{' + self.login + ' : ' + timestamp + '}')
                            else:
                                # добавляем счетшик ошибок
                                self.wrongs.update('{' + self.login + ' : 1 }')

                            # возвращаем ответ-запрет
                            self.connection.sendall(
                                RC5.RC5.encryptBytes('{"authaccess" : { "status" : "false"}}'))

            elif list(jData.keys())[0] == "postauth":
                # проверка почтового кода
                if self.postcode == jData["postauth"]["code"]:
                    # если код совпал то едем дальше
                    self.connection.sendall(RC5.RC5.encryptBytes('{"ostauth" : { "status" : "true"}}'))
                else:
                    # если не совпал, отправляем новый
                    self.postcode = random.randrange(99999999)

                    sent_from = self.gmail_user
                    to = self.emails[self.login]
                    subject = 'Сейф'
                    body = "Ваш проверочный код - " + self.postcode

                    email_text = """\  
                                                From: %s  
                                                To: %s  
                                                Subject: %s

                                                %s
                                                """ % (sent_from, ", ".join(to), subject, body)
                    try:
                        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                        server.ehlo()
                        server.login(self.gmail_user, self.gmail_password)
                        server.sendmail(sent_from, to, email_text)
                        server.close()
                    except:
                        print("Ошибка почты")

                    self.connection.sendall(RC5.RC5.encryptBytes('{"ostauth" : { "status" : "false"}}'))



            elif list(jData.keys())[0] == "getdata":
                # попытка получения информации
                if jData["getdata"]["id"] in list(self.secure_data[self.login].keys()):
                    self.connection.sendall(RC5.RC5.encryptBytes('{"setdata" : { "status" : "true", "data" : ' + self.secure_data[self.login][jData["getdata"]["id"]] + '}}'))
                else:
                    self.connection.sendall(RC5.RC5.encryptBytes('{"setdata": {"status": "false"}}'))
            else:
                # неизвестная команда игнорируется
                pass
            self.connection.sendall(data)
        else :
            self.connection.close()
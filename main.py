import Server

if __name__ == '__main__':
    # создаем єкземпляр сервера
    s = Server.Server("127.0.0.1", 9999)
    # запускаем его
    s.run()
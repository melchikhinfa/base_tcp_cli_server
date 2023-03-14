import socket
import threading
from typing import Dict, Union, Any
from logger import server_logger
from db import UserRegistration
import json

DEF_PORT = 5001


class Server:
    def __init__(self, port):
        server_logger.info("Сервер запускается...")
        self.port = port
        self.sock = None
        self.connections_list = []
        self.user_ip_pair = {}
        server_logger.info(f"Инициализация сервера. Слушает порт:{port}")

        while True:
            conn, address = self.sock.accept()

            self.connections_list.append((conn, address[0]))
            server_logger.info(f"Подключился клиент {address[0]}")
            thr = threading.Thread(target=self.message_logic, args=(conn, address[0]), daemon=True)
            thr.start()

    def socket_init(self):
        sock = socket.socket()
        sock.bind(("", self.port))
        sock.listen(0)
        self.sock = sock

    def send_message(self, conn, data: Union[str, Dict[str, object]], ip: str) -> None:
        """Отправка данных"""
        data_text = data
        if type(data) == dict:
            data = json.dumps(data, ensure_ascii=False)

        data = data.encode()
        conn.send(data)
        server_logger.info(f"Сообщение {data_text} было отправлено клиенту {ip}")

    def message_logic(self, connection, ip_addr):
        data = ""
        while True:
            conn_info = connection.recv(4096)
            data += conn_info.decode()

            if "LF" in data:

                username = self.user_ip_pair[ip_addr]
                server_logger.info(
                    f"Получили сообщение {data} от клиента {ip_addr} ({username})"
                )
                data = {"username": username, "text": data}

                # Рассылка по каждому соединению
                server_logger.info(
                    f"Текущее кол-во подключений к серверу: {len(self.connections_list)}"
                )
                for conn in self.connections_list:
                    current_conn, current_ip = connection
                    try:
                        self.send_message(current_conn, data, current_ip)
                    # Если вдруг у нас появилсоь соедиение, которое уже неактивно
                    except BrokenPipeError:
                        continue
                # Обнуляемся
                data = ""

                # Значит пришла только часть большого сообщения
            else:
                server_logger.info(f"Приняли часть данных от клиента {ip_addr}: '{data}'")

                # Если вообще ничего не пришло - это конец всего соединения
            if not conn_info:
                break




    def getаааа_data(self, conn, ip_addr):
        data = conn.recv(4096).decode()
        server_logger.info(f"Получили данные от клиента {ip_addr}: {data}")
        data = json.loads(data)
        username = data["username"]
        password = data["password"]
        self.user_ip_pair[ip_addr] = username
        server_logger.info(f"Зарегистрировали пользователя {username} с паролем {password} и ip адресом {ip_addr}")
        return username, password, ip_addr

    def run(self):
        self.socket_init()
        while True:
            conn, address = self.sock.accept()
            self.connections_list.append((conn, address[0]))
            server_logger.info(f"Подключился клиент {address[0]}")
            thr = threading.Thread(target=self.message_logic, args=(conn, address[0]), daemon=True)
            thr.start()

    def reg_logic(self, conn, addr):
        """
        Логика регистрации пользователя
        """
        data = json.loads(conn.recv(1024).decode())
        new_pass, new_username = hash(data["password"]), data["username"]
        new_ip = addr[0]
        self.database.user_reg(new_ip, new_pass, new_username)
        server_logger.info(f"Клиент {new_ip} -> регистрация прошла успешно")
        data = {"result": True}
        if new_ip in self.reg_list:
            self.reg_list.remove(new_ip)
            server_logger.info(f"Клиент {new_ip} уже зарегистрирован.")

        self.send_message(conn, data, new_ip)
        server_logger.info(f"Клиент {new_ip}. Отправили данные о результате регистрации")








import socket
import threading
import json
import uuid
import datetime
import sys
from typing import Dict, Union
from logger import server_logger
from auth import UserRegistration
from port_checker import PortValidator
from settings import *



class Server:
    def __init__(self, port):
        server_logger.info("Сервер запускается...")
        self.port = port
        self.sock = None
        self.sessions_list = []
        self.auth_processing = UserRegistration()
        self.socket_init()
        server_logger.info(f"Инициализация сервера. Слушает порт:{port}")

        while True:
            conn, address = self.sock.accept()
            token, est_time = self.generate_token()
            server_logger.info(f"Создан временный токен для клиента {address[0]}")
            self.sessions_list.append((conn, address[0], token, est_time))
            server_logger.info(f"Подключился клиент {address[0]}")
            thr = threading.Thread(target=self.message_logic, args=(conn, address[0]), daemon=True)
            thr.start()

    def socket_init(self):
        sock = socket.socket()
        sock.bind(("", self.port))
        sock.listen(0)
        self.sock = sock

    @staticmethod
    def generate_token():
        token = uuid.uuid4()
        est_time = datetime.datetime.now() + datetime.timedelta(minutes=TOKEN_EST_TIME)
        return token, est_time

    def check_session(self):
        for session in self.sessions_list:
            if session[3] < datetime.datetime.now():
                self.sessions_list.remove(session)
                self.auth_logic(session[0], session[1])
                self.generate_token()
            else:
                continue

    @staticmethod
    def send_message(conn, data: Union[str, Dict[str, object]], ip: str) -> None:
        """Отправка данных"""
        data_text = data
        if type(data) == dict:
            data = json.dumps(data, ensure_ascii=False)
        data = data.encode()
        conn.send(data)
        server_logger.info(f"Сообщение {data_text} было отправлено клиенту {ip}")

    def message_logic(self, conn, ip_addr):
        data = ""
        while True:
            conn_data = conn.recv(4096)
            data += conn_data.decode()
            if "LF" in data:
                username = self.auth_processing.get_info(ip_addr)[1]
                server_logger.info(
                    f"Получили сообщение {data} от клиента {ip_addr} ({username})"
                )
                data = {"username": username, "text": data}
                server_logger.info(
                    f"Текущее кол-во подключений к серверу: {len(self.sessions_list)}"
                )
                for conn in self.sessions_list:
                    current_conn, current_ip = conn[0], conn[1]
                    self.check_session()
                    try:
                        self.send_message(current_conn, data, current_ip)
                    except BrokenPipeError:
                        server_logger.info(f"Клиент {current_ip} отключился")
                        continue
                data = ""
            else:
                server_logger.info(f"Приняли часть данных от клиента {ip_addr}: '{data}'")
            if not conn_data:
                break

    def reg_logic(self, conn, addr):
        conn.sendall("Для регистрации введите следующие данные:".encode())
        conn.sendall("Введите имя пользователя:".encode())
        username = conn.recv(1024).decode()
        conn.sendall("Введите пароль:".encode())
        password = conn.recv(1024).decode()
        if self.auth_processing.userreg(addr, username, password):
            server_logger.info(f"Пользователь {username} зарегистрирован (ip: {addr})")
            conn.sendall("Вы успешно зарегистрированы!".encode())
        else:
            server_logger.info(f"Пользователь c ip: {addr} уже зарегистрирован")
            conn.sendall("Вы уже зарегистрированы.".encode())
            self.auth_logic(conn, addr)

    def auth_logic(self, conn, addr):
        conn.sendall("Для авторизации введите следующие данные:".encode())
        conn.sendall("Введите имя пользователя:".encode())
        username = conn.recv(1024).decode()
        conn.sendall("Введите пароль:".encode())
        password = conn.recv(1024).decode()
        addr = addr[0]
        if self.auth_processing.userauth(addr, username, password) == 1:
            server_logger.info(f"Пользователь {username} авторизован (ip: {addr})")
            conn.sendall("Вы успешно авторизованы!".encode())
        elif self.auth_processing.userauth(addr, username, password) == 0:
            server_logger.info(f"Пользователь {username} ввел неверный пароль (ip: {addr})")
            conn.sendall("Неверный пароль".encode())
        else:
            server_logger.info(f"Пользователь {username} не зарегистрирован (ip: {addr})")
            conn.sendall("Вы не зарегистрированы. Пройдите регистрацию далее.".encode())
            self.reg_logic(conn, addr)

    def handle_logic(self, conn, addr):
        while True:
            addr = addr[0]
            conn.sendall("Выберите действие: reg - регистрация,\
                          auth - авторизация,\
                          exit - выход".encode()
                         )
            data = conn.recv(1024).decode()
            if data == "exit":
                break
            elif data == "reg":
                self.reg_logic(conn, addr)
            elif data == "auth":
                self.auth_logic(conn, addr)
            else:
                conn.sendall("Неверный ввод".encode())

    def client_handle(self, conn, addr):
        ip = addr[0]
        if self.auth_processing.get_info(ip)[3] != 'logged in':
            self.auth_logic(conn, ip)
        elif not self.auth_processing.get_info(ip):
            self.reg_logic(conn, ip)
        else:
            self.message_logic(conn, ip)


def main():
    port_input = input("Введите номер порта для сервера -> ")
    # Тут проверка на то, занят ли порт:
    validator = PortValidator()
    port_flag = validator.port_validation(int(port_input))
    if port_flag:
        server = Server(port_input)
    else:
        print("Порт уже занят")
        sys.exit(1)

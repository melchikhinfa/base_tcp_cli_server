import socket
# import threading
from typing import Dict, Union, Any
from logger import server_logger
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


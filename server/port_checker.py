import socket
import random
from serv_logger import server_logger


ip_addr = "127.0.0.1"

class PortValidator:
    def __int__(self):
        pass

    def port_validation(self, port: int):
        port = int(port)
        if 1023 < port < 65536 and self.check_if_open(port):
            return port
        else:
            server_logger.info(f"Порт {port} занят, генерируем новый свободный порт")
            port = self.generate_free_port()
            return port

    @staticmethod
    def check_if_open(port: int) -> bool:
        port = int(port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if sock.connect_ex((ip_addr, port)) == 0:
            return True
        else:
            return False

    def generate_free_port(self):
        check_flag = False
        while not check_flag:
            port = random.randint(1024, 65535)
            check_flag = self.check_if_open(port)
            return port



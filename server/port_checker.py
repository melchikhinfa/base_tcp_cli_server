import socket


class PortValidator:
    def __int__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = None
        self.ip_addr = 'localhost'

    def port_validation(self, port: int) -> bool:
        port = int(port)
        if 1023 < port < 65536 and self.sock.connect_ex((self.ip_addr, port)) == 0:
            return True
        else:
            return False

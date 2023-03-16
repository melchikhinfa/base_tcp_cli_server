import threading
import socket
from cli_logger import cli_log
import json
from file_partition import read_full_message


class Client:
    def __init__(self, ip_addr: str, port: int) -> None:
        self.host = ip_addr
        self.port = port
        self.sock = None

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        self.sock = sock
        cli_log.info(f"Подключен к серверу {self.host}:{self.port}")
        self.sock.settimeout(1)

    def reg_form(self):
        while True:
            username = input("Введите имя пользователя: ")
            password = input("Введите пароль: ")
            password2 = input("Повторите пароль: ")
            if password == password2 and username != "":
                data = {"username": username, "password": password}
                self.sock.sendall(json.dumps(data).encode())
                server_response = self.sock.recv(1024).decode()
                if server_response == "success":
                    print("Клиент успешно зарегистрирован")
                    cli_log.info(f"Пользователь {username} зарегистрирован на сервере.")
                    break
                elif not server_response:
                    cli_log.info("Сервер не отвечает. Попробуйте позже.")
                    break
                else:
                    print("Пользователь с таким именем уже существует")
                    cli_log.info(f"Пользователь с таким именем уже существует")
                    continue

    def auth_form(self):
        while True:
            username = input("Введите имя пользователя: ")
            password = input("Введите пароль: ")
            data = {"username": username, "password": password}
            if username != "" and password != "":
                self.sock.sendall(json.dumps(data).encode())
                server_response = self.sock.recv(1024).decode()
                if server_response == "success":
                    print("Клиент успешно авторизован")
                    cli_log.info(f"Пользователь {username} авторизован на сервере.")
                    break
                elif server_response == "wrong pass":
                    print("Неверный пароль")
                    cli_log.info(f"Пользователь {username} ввел неверный пароль.")
                    self.connect()
                    continue
                elif server_response == "not registered":
                    print("Пользователь не зарегистрирован. Пожалуйста, зарегистрируйтесь.")
                    self.reg_form()
                    break
                elif not server_response:
                    cli_log.info("Сервер не отвечает. Попробуйте позже.")
                    break
            else:
                print("Поля не должны быть пустыми")
                continue

    def read_message(self):
        while True:
            try:
                data = json.loads(read_full_message(self.sock).decode())
                username, message = data["username"], data["text"]
                print(f"Сообщение от {username}: {message}")
                data = ''
            except IOError:
                cli_log.info("Сервер не отвечает. Попробуйте позже.")
                break

    def send_message(self):
        while True:
            message = input()
            if message == "exit":
                self.sock.close()
                cli_log.info("Пользователь вышел из чата.")
                break
            data = {"username": "user", "text": message}
            self.sock.sendall(json.dumps(data).encode())
            cli_log.info(f"Пользователь отправил сообщение: {message}")
            data = ''

def main():
    client = Client('localhost', 7777)
    client.connect()
    client.auth_form()
    read_thread = threading.Thread(target=client.read_message, daemon=True)
    read_thread.start()
    client.send_message()

if __name__ == "__main__":
    main()




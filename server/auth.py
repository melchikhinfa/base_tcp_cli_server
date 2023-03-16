import sqlite3 as sl
import hashlib
from typing import Any
import db_logger


class UserRegistration:
    def __init__(self):
        self.conn = sl.connect("./data/users.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS \
             users(ip TEXT PRIMARY KEY NOT NULL, name TEXT NOT NULL, password TEXT NOT NULL, status TEXT NOT NULL)"
        )
        db_logger.db_log.info("Подключение к базе данных установлено.")
        self.conn.commit()

    def userreg(self, ip, name, password):
        self.cursor.execute("SELECT * FROM users WHERE ip = ?", (ip,))
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        if self.cursor.fetchone():
            return False
        else:
            self.cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (ip, name, hashed_password))
            db_logger.db_log.info(f"Внесены данные пользователя {name} (ip: {ip}) в базу данных")
            self.conn.commit()
            self.conn.close()
            db_logger.db_log.info("Соединение с базой данных закрыто")
            return True

    def userauth(self, ip, name, password):
        self.cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
        db_passwd = self.cursor.fetchone()[2]
        self.conn.close()
        db_logger.db_log.info("Соединение с базой данных закрыто")
        hashed_user_pass = hashlib.md5(password.encode()).hexdigest()
        if db_passwd == hashed_user_pass:
            self.change_status(ip, 'logged in')
            return 1
        elif db_passwd != hashed_user_pass:
            return 0
        else:
            return -1

    def get_info(self, ip) -> Any:
        self.cursor.execute("SELECT * FROM users WHERE ip = ?", ip)
        user_info = self.cursor.fetchone()
        self.conn.close()
        db_logger.db_log.info("Соединение с базой данных закрыто")
        return user_info

    def change_status(self, ip, status):
        self.cursor.execute("UPDATE users SET status = ? WHERE ip = ?", (status, ip))
        db_logger.db_log.info(f"Обновлена информация о пользователе с ip: {ip}")
        self.conn.commit()
        self.conn.close()
        db_logger.db_log.info("Соединение с базой данных закрыто")



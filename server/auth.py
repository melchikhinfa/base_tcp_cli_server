import sqlite3 as sl
import hashlib
from typing import Any


class UserRegistration:
    def __init__(self):
        self.conn = sl.connect("/data/users.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS \
             users(ip TEXT PRIMARY KEY NOT NULL, name TEXT NOT NULL, password TEXT NOT NULL, status TEXT NOT NULL)"
        )
        self.conn.commit()

    def userreg(self, ip, name, password):
        self.cursor.execute("SELECT * FROM users WHERE ip = ?", (ip,))
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if self.cursor.fetchone():
            return False
        else:
            self.cursor.execute("INSERT INTO users VALUES (?, ?, ?,)", (ip, name, hashed_password, ))

            self.conn.commit()
            self.conn.close()
            return True

    def userauth(self, ip, name, password):
        self.cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
        passwd = self.cursor.fetchone()[2]
        self.conn.close()
        if passwd == password:
            self.change_status(ip, 'logged in')
            return 1
        elif passwd != password:
            return 0
        else:
            return -1

    def get_info(self, ip) -> Any:
        self.cursor.execute("SELECT * FROM users WHERE ip = ?", (ip, ""))
        user_info = self.cursor.fetchone()
        self.conn.close()
        return user_info

    def change_status(self, ip, status):
        self.cursor.execute("UPDATE users SET status = ? WHERE ip = ?", (status, ip))
        self.conn.commit()
        self.conn.close()

    def __del__(self):
        self.conn.close()

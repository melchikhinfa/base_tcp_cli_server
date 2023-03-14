import sqlite3 as sl
import hashlib


class UserRegistration:
    def __init__(self):
        self.name = None
        self.password = None
        self.ip = None
        self.conn = sl.connect("/data/users.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT NOT NULL, name TEXT NOT NULL, password TEXT NOT NULL)")

    def usereg(self, ip, name, password):
        self.cursor.execute("SELECT * FROM users WHERE ip = ?", (ip,))
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if self.cursor.fetchone():
            return False
        else:
            self.cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (self.ip, self.name, hashed_password))
            self.conn.commit()
            return True

    def userauth(self, ip, name, password):
        self.cursor.execute("SELECT * FROM users WHERE ip = ?", (ip,))
        if self.cursor.fetchone():
            return True
        else:
            return False




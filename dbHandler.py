import sqlite3
import logging
class DbHandler:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_table()


    def create_table(self):
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS disk_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    instance_id TEXT,
                                    DiskUsage REAL,
                                    MountPoint TEXT
                                )''')
            self.conn.commit()
            print("Create Table Successful")
        except Exception as e:
            print(str(e))

    def insert_data(self, data):
        try:
            self.cursor.execute("INSERT INTO disk_usage (instance_id, DiskUsage, MountPoint) VALUES (?, ?, ?)",
                            (data["instance_id"], data["DiskUsage"], data["MountPoint"]))
            self.conn.commit()
        except Exception as e:
            print(str(e))

    def close_connection(self):
        self.conn.close()
import sqlite3
import logging
class DbHandler:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_diskusage_table()
        self.create_cpuusage_table()
        self.dblogger =self.create_logger()

    def create_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s",'%Y-%m-%d %H:%M:%S')
        file_handler = logging.FileHandler("/tmp/appdb.log")
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        return logger

    def create_diskusage_table(self):
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS disk_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    instance_id TEXT,
                                    DiskUsage REAL,
                                    MountPoint TEXT
                                )''')
            self.conn.commit()
        except Exception as e:
            self.dblogger("DB Error, create_diskusage_table: " + str(e))

    def create_cpuusage_table(self):
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS cpu_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    instance_id TEXT,
                                    cpuusage REAL,
                                    asgname TEXT
                                )''')
            self.conn.commit()
        except Exception as e:
            self.dblogger("DB Error, create_cpuusage_table: " + str(e))

    def insert_diskusage_data(self, data):
        try:
            self.cursor.execute("INSERT INTO disk_usage (instance_id, DiskUsage, MountPoint) VALUES (?, ?, ?)",
                            (data["instance_id"], data["DiskUsage"], data["MountPoint"]))
            self.conn.commit()
        except Exception as e:
            self.dblogger("DB Error, insert_diskusage_data: " + str(e))

    def insert_cpuusage_data(self, data):
        try:
            self.cursor.execute("INSERT INTO cpu_usage (instance_id, cpuusage, asgname) VALUES (?, ?, ?)",
                            (data["instance_id"], data["cpuusage"], data["asgname"]))
            self.conn.commit()
        except Exception as e:
            self.dblogger("DB Error, insert_diskusage_data: " + str(e))

    def close_connection(self):
        try:
            self.conn.close()
        except Exception as e:
            self.dblogger("DB Error, close_connection: " + str(e))
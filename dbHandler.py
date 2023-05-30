import sqlite3
import logging
class DbHandler:
    #timestamps in utc will be added automatically
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_diskusage_table()
        self.create_cpuusage_table()
        self.create_memusage_table()
        self.dblogger = self.create_logger()

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
                                    MountPoint TEXT,
                                    asg_name TEXT,
                                    region_name TEXT,
                                    updatedat CURRENT_TIMESTAMP
                                )''')
            self.conn.commit()
        except Exception as e:
            self.dblogger.warning("DB Error, create_diskusage_table: " + str(e))

    def create_memusage_table(self):
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS mem_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    instance_id TEXT,
                                    public_ip TEXT,
                                    memusage REAL,
                                    total_memory REAL ,
                                    asg_name TEXT,
                                    region_name TEXT,
                                    updatedat CURRENT_TIMESTAMP
                                )''')
            self.conn.commit()
        except Exception as e:
            self.dblogger.warning("DB Error, create_memusage_table: " + str(e))
    def insert_memusage_data(self, data):
        try:
            self.cursor.execute("INSERT INTO mem_usage (instance_id,public_ip, memusage,total_memory, asgname,region_name) VALUES (?,?,?,?,?,?)",
                            (data["instance_id"], data["public_ip"], data["memusage"],data["total_memory"], data["asgname"],data["region_name"]))
            self.conn.commit()
        except Exception as e:
            self.dblogger.warning("DB Error, insert_memusage_data: " + str(e))

    def create_cpuusage_table(self):
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS cpu_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    instance_id TEXT,
                                    cpuusage REAL,
                                    asgname TEXT,
                                    region_name TEXT,
                                    updatedat CURRENT_TIMESTAMP
                                )''')
            self.conn.commit()
        except Exception as e:
            self.dblogger.warning("DB Error, create_cpuusage_table: " + str(e))

    def insert_diskusage_data(self, data):
        try:
            self.cursor.execute("INSERT INTO disk_usage (instance_id, DiskUsage, MountPoint,asg_name,region_name) VALUES (?, ?, ?,?,?)",
                            (data["instance_id"], data["DiskUsage"], data["MountPoint"],data["asg_name"],data["region_name"]))
            self.conn.commit()
        except Exception as e:
            self.dblogger.warning("DB Error, insert_diskusage_data: " + str(e))

    def insert_cpuusage_data(self, data):
        try:
            self.cursor.execute("INSERT INTO cpu_usage (instance_id, cpuusage, asgname) VALUES (?, ?, ?)",
                            (data["instance_id"], data["cpuusage"], data["asgname"]))
            self.conn.commit()
        except Exception as e:
            self.dblogger.warning("DB Error, insert_memusage_data: " + str(e))



    def close_connection(self):
        try:
            self.conn.close()
        except Exception as e:
            self.dblogger.warning("DB Error, close_connection: " + str(e))
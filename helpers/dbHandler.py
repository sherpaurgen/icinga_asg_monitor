#!/monitoringScripts/VENVT/bin/python
import sqlite3
import logging
class DbHandler:
    #timestamps in utc will be added automatically
    def __init__(self, db_file):
        self.db_file_path=db_file
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
    def create_cpuusage_table(self):
        try:
            conn = sqlite3.connect(self.db_file_path)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS cpu_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    instance_id TEXT,
                                    instance_name TEXT,
                                    public_ip TEXT,
                                    private_ip TEXT,
                                    cpu_usage REAL,
                                    asg_name TEXT,
                                    region_name TEXT,
                                    updatedat TEXT DEFAULT CURRENT_TIMESTAMP
                                )''')
            conn.commit()
            conn.close()
        except Exception as e:
            self.dblogger.warning("DB Error, create_cpuusage_table: " + str(e))
    def create_memusage_table(self):
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS mem_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    instance_id TEXT,
                                    asg_name TEXT,
                                    region_name TEXT,
                                    mem_used REAL,
                                    updatedat TEXT DEFAULT CURRENT_TIMESTAMP
                                )''')
            self.conn.commit()
            self.conn.close()
        except Exception as e:
            self.dblogger.warning("DB Error, create_memusage_table: " + str(e))

    def insert_memusage_data(self, data):
        conn = sqlite3.connect(self.db_file_path)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO mem_usage (instance_id, asg_name,region_name,mem_used) VALUES (?,?,?,?)",
                            (data["instance_id"], data["asg_name"],data["region_name"],data["mem_used"]))
            conn.commit()
            conn.close()
        except Exception as e:
            self.dblogger.warning("DB Error, insert_memusage_data: " + str(e))

    def truncate_table(self):
        conn = sqlite3.connect(self.db_file_path)
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM cpu_usage")
            cursor.execute("DELETE FROM mem_usage")
            cursor.execute("DELETE FROM disk_usage")
            conn.commit()
            conn.close()
        except Exception as e:
            self.dblogger.warning("DB Error, Truncate tables: " + str(e))



    def insert_diskusage_data(self, data):
        try:
            self.cursor.execute("INSERT INTO disk_usage (instance_id, DiskUsage, MountPoint,asg_name,region_name) VALUES (?, ?, ?,?,?)",
                            (data["instance_id"], data["DiskUsage"], data["MountPoint"],data["asg_name"],data["region_name"]))
            self.conn.commit()
        except Exception as e:
            self.dblogger.warning("DB Error, insert_diskusage_data: " + str(e))

    def insert_cpuusage_data(self,data):
        conn = sqlite3.connect(self.db_file_path)
        cursor = conn.cursor()
        self.create_cpuusage_table()
        try:
            cursor.execute("INSERT INTO cpu_usage (instance_id,instance_name,public_ip,private_ip,cpu_usage,asg_name,region_name) VALUES (?, ?, ?, ?,? ,?,?)",
                            (data["instance_id"],data["instance_name"],data["public_ip"],data["private_ip"], data["cpuusage"], data["asg_name"],data["region_name"]))
            conn.commit()
            conn.close()
        except Exception as e:
            self.dblogger.warning("DB Error, insert_cpu_usage_data: " + str(e))


    def close_connection(self):
        try:
            self.conn.close()
        except Exception as e:
            self.dblogger.warning("DB Error, close_connection: " + str(e))
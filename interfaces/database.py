import config.config as config
import sqlite3


class DBHandler:

    """ __init__ is called on initialization of every new DBHandler """
    def __init__(self):
        parameters = config.config["db"]
        self.db_file = parameters["file"]

    def settings(self) -> str:
        return self.db_file

    def write_loc_to_db(self, new_entry: tuple):
        con = sqlite3.connect(self.db_file)
        cursor = con.cursor()
        # create_gps_data_format = """CREATE TABLE IF NOT EXISTS
        #                    location_and_time(id INTEGER, location TEXT, time TEXT)"""
        # cursor.execute(create_gps_data_format)
        cursor.execute("""INSERT INTO location_and_time(id, location, time) VALUES(?, ?, ?)""", new_entry)
        con.commit()
        con.close()

    def read_loc_db(self) -> list:
        con = sqlite3.connect(self.db_file)
        cursor = con.cursor()
        cursor.execute('SELECT * FROM location_and_time')
        print("trying to fetch entries")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        return rows

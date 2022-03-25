import config.config as config
import sqlite3


class DBInterface:
    """ __init__ is called on initialization of every new DBHandler """

    def __init__(self):
        parameters = config.config["db"]
        self.db_file = parameters["file"]
        self.make_table()
        self.gps_index = self.fetch_gps_index()[0]


    """ settings returns the current name of the .db file """

    def settings(self) -> str:
        return self.db_file

    def make_table(self):
        con = sqlite3.connect(self.db_file)
        cursor = con.cursor()
        create_gps_data_format = """CREATE TABLE IF NOT EXISTS
                                   location_and_time(id INTEGER, location TEXT, time TEXT)"""
        cursor.execute(create_gps_data_format)
        con.commit()
        con.close()

    def fetch_gps_index(self):
        conn = sqlite3.connect(self.db_file)  # Connecting to sqlite
        cursor = conn.cursor()  # Creating a cursor object using the cursor() method
        cursor.execute('''SELECT id from location_and_time ORDER BY id DESC LIMIT 1''')  # Retrieving data
        result = cursor.fetchone()  # Fetching 1st row from the table
        conn.close()  # Closing the connection
        if result is None:
            return 0, 0
        return result

    """ write_loc_to_db writes the passed tuple to the location and time table in the database"""

    def write_loc_to_db(self, new_entry: tuple):
        con = sqlite3.connect(self.db_file)
        cursor = con.cursor()
        create_gps_data_format = """CREATE TABLE IF NOT EXISTS
                           location_and_time(id INTEGER, location TEXT, time TEXT)"""
        cursor.execute(create_gps_data_format)
        cursor.execute("""INSERT INTO location_and_time(id, location, time) VALUES(?, ?, ?)""", new_entry)
        con.commit()
        con.close()

    """ read_loc_db returns all of the entries in the location and time table of the database """

    def read_loc_db(self) -> list:
        con = sqlite3.connect(self.db_file)
        cursor = con.cursor()
        cursor.execute('SELECT * FROM location_and_time')
        print("trying to fetch entries")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        return rows

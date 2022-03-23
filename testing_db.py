import config.config as config
from interfaces.database import DBHandler
from testing_db_ext import get_location_and_time

config.set_specific("db", "file", "gps.db")
db = DBHandler()

loc_and_time = (1, "harrisonburg", "10pm")

db.write_loc_to_db(new_entry=loc_and_time)


rows = get_location_and_time()
for row in rows:
    print(row)

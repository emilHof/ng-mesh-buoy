import config.config as config
from interfaces.radio import RadioInterface
from interfaces.gps import GPSInterface
from interfaces.database import DBInterface
from handlers.message_handler import MessageHandler


def db_fetch_and_send_test():
    config.set_specific("db", "file", "local_data.db")
    fetch_string = "@turb_get_bulk_5_"

    msgHandler = MessageHandler()

    rows = msgHandler.get_bulk_data(fetch_string)

    for row in rows:
        print(row)

db_fetch_and_send_test()


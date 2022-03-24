import config.config as config
from interfaces.database import DBHandler


def get_location_and_time() -> list:
    db = DBHandler()

    rows = db.read_loc_db()

    return rows

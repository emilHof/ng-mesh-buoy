import asyncio
import datetime
import time

import config.config as config
from interfaces.radio import RadioInterface
from interfaces.gps import GPSInterface, time_dif_gps, get_time_sync
from interfaces.database import DBInterface
from handlers.message_handler import MessageHandler


def db_fetch_test():
    config.set_specific("db", "file", "local_data.db")
    fetch_string = "@turb_get_bulk_5_"

    msgHandler = MessageHandler()

    rows = msgHandler.get_bulk_data(fetch_string)

    for row in rows:
        print(row)


async def time_stamp_test():
    config.set_specific("db", "file", "local_data.db")
    config.set_specific("gps", "port", "/dev/ttyUSB0")
    config.set_specific("gps", "rate", 9600)

    gps = GPSInterface()
    test_time = await gps.set_onboard_time()

    # try time math
    sleep_time = 2
    gps_time = await gps.get_time_non_conv()
    time.sleep(sleep_time)
    proces_time = datetime.datetime.now() + datetime.timedelta(hours=4)
    time_delta = time_dif_gps(gps_time, proces_time)

    accepted_difference = [
        datetime.time(0, 0, (sleep_time - 1) % 60),
        datetime.time(0, 0, sleep_time % 60),
        datetime.time(0, 0, (sleep_time + 1) % 60),
    ]

    fail_counter = 0
    for diff in accepted_difference:
        if time_delta != diff:
            fail_counter += 1

    if fail_counter == 3:
        print("Failed Test!")
        return

    time_now = get_time_sync()

    now = datetime.datetime.now() + datetime.timedelta(hours=4)

    local_time_now = datetime.time(now.hour, now.minute, now.second)

    print(local_time_now, time_now)

    print("test passed!")


# db_fetch_test()

async def main():
    await time_stamp_test()


if __name__ == "__main__":
    asyncio.run(main())

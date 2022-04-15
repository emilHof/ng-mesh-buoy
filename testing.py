import asyncio
import datetime
import time

import config.config as config
from interfaces.radio import RadioInterface
from interfaces.gps import GPSInterface, time_dif_gps, get_time_sync
from interfaces.database import DBInterface
from handlers.message_handler import MessageHandler, check_dep_queue


def db_fetch_test():
    config.set_specific("db", "file", "local_data.db")
    fetch_string = "@rfid_get_bulk_5_"

    msgHandler = MessageHandler(gps=False, radio=False)

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


async def bulk_radio_fetch_test(n, k):
    config.set_specific("radio", "port", "/dev/ttyUSB2")
    config.set_specific("radio", "rate", 9600)
    config.set_specific("db", "file", "local_data.db")

    xbee = RadioInterface()
    msg_handler = MessageHandler(gps=False, radio=True)
    msg_handler.connect_radio()

    avg_dif = float(0.0)

    start = datetime.datetime.now()

    while k != 0:
        xbee.send_test_string("@rturb_get_bulk_" + str(n) + "_")
        rows = await msg_handler.propagate_message(debug=True)

        dif = float(n - len(rows))
        avg_dif = (avg_dif + dif) / 2

        k -= 1

        time.sleep(3)

    stop = datetime.datetime.now()

    trans_time = stop - start

    if avg_dif > 2.5:
        print("bulk_radio_fetch_test test FAILED with an average of"
              " {} packets dropped in {} seconds".format(str(avg_dif), str(trans_time.seconds)))

    print("bulk_radio_fetch_test test PASSED with an average of"
          " {} packets dropped in {} seconds".format(str(avg_dif), str(trans_time.seconds)))


def test_dep_queue(test_array: []):
    for i in test_array:
        config.enqueue_dep_queue(i)

    messages = check_dep_queue()

    for i in range(len(test_array)):
        if messages[i] != test_array[i]:
            print("test_dep_queue FAILED. {} does not equal {}".format(messages[i], test_array[i]))

    print("test_dep_queue PASSED")


async def main():
    test_dep_queue(["2", "hello", "three"])


if __name__ == "__main__":
    asyncio.run(main())

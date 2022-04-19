import asyncio
import datetime
import time

import config.config as config
from interfaces.radio import RadioInterface
from interfaces.gps import GPSInterface, time_dif_gps, get_time_sync
from interfaces.database import DBInterface
from pkg.handlers.message_handler import MessageHandler


def db_fetch_test():
    config.set_specific("db", "file", "local_data.db")
    fetch_string = "@rfid_get_bulk_5_"

    msgHandler = MessageHandler(gps=False)

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


async def test_message_handling(test_packet: list, debug: bool = False):
    config.set_specific("db", "file", "local_data.db")

    in_queue = asyncio.Queue()
    dep_queue = asyncio.Queue()

    msg_handler = MessageHandler(in_queue, dep_queue)

    workers = [
        asyncio.create_task(receiver(test_packet, in_queue)),
        asyncio.create_task(msg_handler.handle_msg())
    ]

    res = await asyncio.gather(
        asyncio.create_task(sender(dep_queue)),
    )
    out_packet = res[0]
    if debug: print("outbound packet complete")

    await in_queue.join()
    if debug: print("all tasks are processed")

    for worker in workers:
        worker.cancel()
    if debug: print("workers canceled")

    for i in range(len(out_packet)):
        if out_packet[i] != test_packet[i]:
            print(f'test failed at messages {out_packet[i]} and {test_packet[i]}')
            return

    print("test passed!")
    return


async def receiver(msgs: list, in_q: asyncio.Queue, debug: bool = False):
    for msg in msgs:
        in_q.put_nowait(msg)
        if debug: print(f'message sent: {msg}')
        await asyncio.sleep(.25)


async def sender(dep_q: asyncio.Queue, debug: bool = False) -> list:
    out_msgs = []

    while True:
        task = await dep_q.get()
        out_msg, sleep_time = task[0], task[1]

        if debug: print(f'msg sent: {out_msg}')
        out_msgs.append(out_msg)
        dep_q.task_done()

        if out_msg == "--end":
            return out_msgs

        await asyncio.sleep(.35)


async def test_bulk_handling(bulk_request: list, debug: bool = False):
    config.set_specific("db", "file", "local_data.db")

    in_queue = asyncio.Queue()
    dep_queue = asyncio.Queue()

    msg_handler = MessageHandler(in_queue, dep_queue)
    db = DBInterface()

    rf = db.read_db("turb", 5)
    reference_rows = ["@inc_block"]

    for row in reversed(rf):
        reference_rows.append(str(row[0]) + " " + row[1] + " " + row[2])

    reference_rows.append("--end")

    workers = [
        asyncio.create_task(receiver(bulk_request, in_queue)),
        asyncio.create_task(msg_handler.handle_msg(debug=debug))
    ]

    res = await asyncio.gather(
        asyncio.create_task(sender(dep_queue)),
    )

    res = res[0]

    await in_queue.join()

    for worker in workers:
        worker.cancel()

    for i in range(len(res)):
        if res[i] != reference_rows[i]:
            print(f'test failed at {res[i]} and {reference_rows[i]} !')
            return

    print("test_bulk_handling passed !")


async def test_handle_block(debug: bool = False):
    config.set_specific("db", "file", "local_data.db")

    in_queue = asyncio.Queue()
    dep_queue = asyncio.Queue()

    msg_handler = MessageHandler(in_queue, dep_queue)
    db = DBInterface()

    rf = db.read_db("turb", 5)
    reference_rows = ["@inc_block"]

    for row in reversed(rf):
        reference_rows.append(str(row[0]) + " " + row[1] + " " + row[2])

    reference_rows.append("--end")

    workers = [
        asyncio.create_task(receiver(reference_rows, in_queue)),
        asyncio.create_task(msg_handler.handle_msg(debug=debug))
    ]

    await asyncio.gather(workers[0])

    # out_rows = out[1]
    # reference_rows = reference_rows[1:]

    await in_queue.join()

    if debug: print(f'in_queue joined')

    for worker in workers:
        worker.cancel()

    # for i, _ in out_rows:
    #     if out_rows[i] != reference_rows[i]:
    #         print(f'test failed at {out_rows[i]} and {reference_rows[i]}')


async def main():
    # await test_bulk_handling(["@5_get_bulk_turb", "--end"], debug=False)
    await test_handle_block(debug=False)


if __name__ == "__main__":
    asyncio.run(main())

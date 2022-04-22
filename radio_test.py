import asyncio

from interfaces.radio import RadioInterface
from pkg.msgs.msg_types import SimpleMessage
from pkg.handlers.message_handler import MessageHandler


class FalsePacket:
    def __init__(self):
        self.id = "hi"
        self.msg = "yoyoyoy"


msgs: list[SimpleMessage] = [
    SimpleMessage("00", "hello there!", "4054"),
    SimpleMessage("00", "whats good!", "7405"),
    SimpleMessage("00", "hello people!", "1043")
]


async def msg_object_printer(in_queue: asyncio.Queue):
    while True:
        msg_obj = await in_queue.get()
        print("from the in_queue:")
        print(f'id: {msg_obj.ni} \n' +
              f'msg: {msg_obj.msg} \n' +
              f'time_hash: {msg_obj.time_hash} \n'
              )

        in_queue.task_done()


async def test_receive_callback():
    in_queue = asyncio.Queue()

    radio = RadioInterface(close_chan=in_queue, in_queue=in_queue, dep_queue=in_queue, test=True)

    for m in msgs:
        radio.test_receive_callback_with_decode(m)

    false_msg = FalsePacket()

    radio.test_receive_callback_with_decode(false_msg)

    printer = asyncio.Task(msg_object_printer(in_queue))

    await in_queue.join()

    printer.cancel()
    return


async def main():
    await test_receive_callback()


if __name__ == "__main__":
    asyncio.run(main())

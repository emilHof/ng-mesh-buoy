import asyncio

from cli import RadioCLI


async def receiver(msgs: list, in_q: asyncio.Queue, debug: bool = False):
    for msg in msgs:
        in_q.put_nowait(msg)
        if debug: print(f'message received: {msg}')
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


async def router(dep_queue: asyncio.Queue, in_queue: asyncio.Queue):
    while True:
        msg = await dep_queue.get()
        in_queue.put_nowait(msg)


async def printer(in_queue: asyncio.Queue, print_queue: asyncio.Queue):
    while True:
        msg = await in_queue.get()
        print_queue.put_nowait(msg)


async def test_cli_send_message():
    dep_queue = asyncio.Queue()
    in_queue = asyncio.Queue()
    print_queue = asyncio.Queue()

    cli = RadioCLI(dep_queue, print_queue)

    await asyncio.gather(cli.cli(), router(dep_queue, in_queue), printer(in_queue, print_queue))


async def main():
    await test_cli_send_message()


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import datetime

from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit import prompt


class RadioCLI:
    def __init__(self, dep_queue: asyncio.Queue, print_queue: asyncio.Queue):
        self.dep_queue = dep_queue
        self.print_queue = print_queue
        self.func_dict = {
            "send-msg": self.send_msg,
            "print-data": self.print_data
        }

    async def cli(self):
        while True:
            # Create Prompt.
            session = PromptSession("What would you like to do? (send-msg, wait-for-data, print-data) ")

            # read the message the user want to send
            while True:
                try:
                    user_input = await session.prompt_async()

                    if user_input in self.func_dict:
                        await self.func_dict[user_input]()
                    elif user_input == "q":
                        exit(0)

                except (EOFError, KeyboardInterrupt):
                    return

    async def send_msg(self):
        session = PromptSession("Type your message: ")

        user_input = await session.prompt_async()

        c_time = datetime.datetime.now().strftime("%H:%M:%S")

        self.dep_queue.put_nowait((user_input, 0, c_time))

    async def print_data(self):
        while not self.print_queue.empty():
            print(self.print_queue.get_nowait())

            self.print_queue.task_done()
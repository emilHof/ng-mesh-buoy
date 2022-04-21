import asyncio
import datetime

from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit import prompt


async def def_target():
    session = PromptSession("To which node would you like to send? (eg: 02) ")

    user_input = await session.prompt_async()

    return user_input


def make_cmd_message(msg: str, target: str) -> tuple:
    c_time = datetime.datetime.now().strftime("%H:%M:%S")

    comp_msg = f't:{target},{msg}'

    return comp_msg, 0, c_time


class RadioCLI:
    def __init__(self, dep_queue: asyncio.Queue, print_queue: asyncio.Queue):
        self.dep_queue = dep_queue
        self.print_queue = print_queue
        self.func_dict = {
            "send-msg": self.__send_msg,
            "print-data": self.print_data
        }

    async def cli(self):
        while True:
            # Create Prompt.
            session = PromptSession("What would you like to do? (type help for examples) ")

            # read the message the user want to send
            while True:
                try:
                    user_input = await session.prompt_async()

                    if user_input in self.func_dict:
                        await self.func_dict[user_input]()
                    elif user_input == "help":
                        print("Sample commands:")
                        print('\x1b[6;30;42m' + 'send-msg' + '\x1b[0m' + " (send a message)")
                        print('\x1b[6;30;42m' + 'print-data' + '\x1b[0m' + " (print received data to the screen)")
                        print('\x1b[6;30;42m' + 'q' + '\x1b[0m' + " (quit)")
                    elif user_input == "q":
                        exit(0)

                except (EOFError, KeyboardInterrupt):
                    return

    async def __send_msg(self):
        session = PromptSession("Type your message: ")

        user_input = await session.prompt_async()
        target = await def_target()

        packet = make_cmd_message(user_input, target)

        self.dep_queue.put_nowait(packet)

    async def print_data(self):
        print("-----------DATA-----------")
        while not self.print_queue.empty():
            print(self.print_queue.get_nowait())

            self.print_queue.task_done()
        print("------------END!----------")

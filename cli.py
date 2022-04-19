import asyncio

import config.config as config
from interfaces.radio import RadioInterface
from pkg.handlers.message_handler import MessageHandler
from pkg.ui.cli import RadioCLI

radio_settings = {
    "port": "/dev/ttyUSB2",
    "rate": 9600,
}

gps_settings = {
    "port": "/dev/ttyUSB4",
    "rate": 9600,
}

db_setting = {
    "file": "local_data.db"
}


async def main():
    config.set_config(radio_dict=radio_settings, gps_dict=gps_settings, db_dict=db_setting)
    config.set_specific("NI", "ni", "01")

    in_queue = asyncio.Queue()
    dep_queue = asyncio.Queue()
    print_queue = asyncio.Queue()

    radio = RadioInterface(in_queue, dep_queue)
    msg_handler = MessageHandler(in_queue, dep_queue, gps=False)
    cli = RadioCLI(dep_queue, print_queue)

    # set up an asynchronous loop to propagate messages and listen for rfid signals
    await asyncio.gather(
        msg_handler.handle_msg(),
        radio.listen(debug=True),
        radio.send(debug=True),
        cli.cli()
    )

    return "all async loops exited"


if __name__ == "__main__":
    output = asyncio.run(main())
    print(output)

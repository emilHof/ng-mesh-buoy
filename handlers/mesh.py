import interfaces.radio_interface as radio_interface
from datetime import datetime


def add_time_stamp():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time


def mesh_to_all(message):
    radio_interface.relay_message(message + " " + add_time_stamp())


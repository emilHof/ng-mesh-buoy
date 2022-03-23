import serial
import config.config as config


class Port:
    def __init__(self, specific_type):
        self.specific_type = config.config[specific_type]
        self.uart = serial.Serial(self.specific_type["port"], baudrate=self.specific_type["rate"], timeout=10)
        print("new port made with", self.specific_type["port"], self.specific_type["rate"])

    def print_settings(self):
        print(self.specific_type["port"], self.specific_type["rate"])

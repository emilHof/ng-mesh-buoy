class MessageHandler:
    def __init__(self, radio, gps):
        self.radio = radio
        self.gps = gps

    def handle_message(self, message):
        if message.startswith("@get_location"):
            location = self.gps.get_location
            self.radio.send_back(location)
        else:
            return "command unknown!"

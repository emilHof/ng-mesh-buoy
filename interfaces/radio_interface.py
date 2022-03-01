import externals.radio.radio_transmitter as radio_transmitter


def relay_message(message):
    radio_transmitter.broadcast_all(message)

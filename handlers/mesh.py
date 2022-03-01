import interfaces.radio_interface as radio_interface


def mesh_to_all(message):
    radio_interface.relay_message(message)
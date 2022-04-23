class SimpleMessage(object):
    """
    SimpleMessage is a JSON compatible object that holds packet information,
    such as Node ID, Message, & Time Hash
    """

    def __init__(self, ni: str, msg: str, time_hash: str):
        self.ni = ni
        self.msg = msg
        self.time_hash = time_hash

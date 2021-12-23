from Objects.MyObject import MyObject


class Exchange(MyObject):
    def __init__(self, *values):
        self.id = values[0]
        self.person_id = values[1]
        self.name = values[2].decode('UTF-8') if type(values[2]) is bytes else values[2]
        self.api_key = values[3].decode('UTF-8') if type(values[3]) is bytes else values[3]
        self.api_secret = values[4].decode('UTF-8') if type(values[4]) is bytes else values[4]
        self.api_passphrase = values[5].decode('UTF-8') if type(values[5]) is bytes else values[5]
        self.api_sandbox = values[6]

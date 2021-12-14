import json

from Objects.MyObject import MyObject


class RawButton(MyObject):

    def __init__(self, *values):
        self.button_id = values[0]
        self.button_text = values[1].decode('UTF-8') if type(values[1]) is bytes else values[1]
        self.button_admin_key = values[2]
        self.button_messages = json.loads(values[3]) if values[3] is not None else None
        self.button_belong_to = values[4]
        self.button_keyboards = json.loads(values[5]) if values[5] is not None else None
        self.button_special_keyboards = json.loads(values[6]) if values[6] is not None else None

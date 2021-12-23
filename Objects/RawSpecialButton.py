from Objects.MyObject import MyObject


class RawSpecialButton(MyObject):
    def __init__(self, *values):
        self.special_button_id = values[0]
        self.special_button_text = values[1].decode('UTF-8') if type(values[1]) is bytes else values[1]
        self.special_button_admin_key = values[2]

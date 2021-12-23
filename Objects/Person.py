from Objects.MyObject import MyObject


class Person(MyObject):
    def __init__(self, *values):
        self.person_id = values[0]
        self.person_chat_id = values[1]
        self.person_first_name = values[2].decode('UTF-8') if type(values[2]) is bytes else values[2]
        self.person_last_name = values[3].decode('UTF-8') if type(values[3]) is bytes else values[3]
        self.person_username = values[4].decode('UTF-8') if type(values[4]) is bytes else values[4]
        self.person_progress = values[5] if values[5] is not (None or "") else None
        self.person_is_admin = values[6]
        self.person_last_button_id = values[7]
        self.person_last_special_button_id = values[8]

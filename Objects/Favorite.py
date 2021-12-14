from Objects.MyObject import MyObject


class Favorite(MyObject):
    def __init__(self, *values):
        self.favorite_id = values[0]
        self.favorite_person_id = values[1]
        self.favorite_exchange = values[2]
        self.favorite_currency = values[3].decode('UTF-8') if type(values[3]) is bytes else values[3]
        self.favorite_base = values[4].decode('UTF-8') if type(values[4]) is bytes else values[4]

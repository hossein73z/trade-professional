from Objects.MyObject import MyObject


class Favorite(MyObject):
    def __init__(self, *values):
        self.favorite_id = values[0]
        self.favorite_person_id = values[1]
        self.favorite_exchange_order_id = values[2]
        self.favorite_exchange = values[3]
        self.favorite_currency = values[4].decode('UTF-8') if type(values[4]) is bytes else values[4]
        self.favorite_base = values[5].decode('UTF-8') if type(values[5]) is bytes else values[5]
        self.favorite_price = values[6]
        self.favorite_amount = values[7]
        self.favorite_value = values[8]
        self.favorite_is_active = values[9]
        self.favorite_trade = values[10]

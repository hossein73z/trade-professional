from Objects.MyObject import MyObject


class Order(MyObject):
    def __init__(self, *values):
        self.order_id = values[0]
        self.order_person_id = values[1]
        self.order_exchange_order_id = values[2].decode('UTF-8') if type(values[2]) is bytes else values[2]
        self.order_exchange = values[3]
        self.order_currency = values[4].decode('UTF-8') if type(values[4]) is bytes else values[4]
        self.order_base = values[5].decode('UTF-8') if type(values[5]) is bytes else values[5]
        self.order_price = values[6]
        self.order_amount = values[7]
        self.order_value = values[8]
        self.order_datetime = values[9]
        self.order_is_active = values[10]
        # self.order_trade = values[10]

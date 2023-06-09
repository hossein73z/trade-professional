from kucoin.client import Client
from prettytable import PrettyTable

from Functions.DatabaseCRUD import read, raw_buttons_table
from Objects.RawButton import RawButton


class FormatText:
    def __init__(self):
        pass

    @staticmethod
    def create_table_for_pairs(client: Client, field_names: list[str], value_list: list, alignment_dict: dict):
        pretty_table = PrettyTable()
        pretty_table.field_names = field_names
        if alignment_dict is not None:
            for alignment in alignment_dict:
                pretty_table.align[alignment] = alignment_dict[alignment]
        for value in value_list:
            ticker = client.get_ticker(f'{value.favorite_currency}-{value.favorite_base}')
            if ticker is not None:
                pretty_table.add_row(
                    [f"{value.favorite_currency}/{value.favorite_base}", ticker['price']])

        return pretty_table

    @staticmethod
    def create_table_for_exchanges(field_names: list[str], value_list: list, alignment_dict: dict):
        pretty_table = PrettyTable()
        pretty_table.field_names = field_names
        if alignment_dict is not None:
            for alignment in alignment_dict:
                pretty_table.align[alignment] = alignment_dict[alignment]
        for value in value_list:
            pretty_table.add_row([value['name'], value['balance']])

        return pretty_table

    @staticmethod
    def button_map(received_button_id):
        buttons: list[RawButton] = read(raw_buttons_table, RawButton)
        buttons_dict = {}
        for button in buttons:
            buttons_dict[button.button_id] = button

        button = buttons_dict[received_button_id]
        sub_button_list = []
        button_list = []
        belong_to = None
        while button.button_belong_to is not None:
            button = buttons_dict[button.button_belong_to]
            for button_id_array in button.button_keyboards:
                for button_id in button_id_array:
                    button_list.append(buttons_dict[button_id].button_text)
                    if button_id == received_button_id:
                        button_list.append('You Are Here')
                    if button_id == belong_to:
                        button_list.append(sub_button_list)
                        sub_button_list = []

            belong_to = button.button_id
            sub_button_list = button_list
            button_list = []

        def printing(text_list, space='➖'):
            text = ''
            for item in text_list:
                if type(item) == list:
                    index = text.rfind('➖')
                    text = text[:index] + "➕" + text[index + 1:] if not index < 0 else text
                    text += printing(item, '    ' + space)
                elif item == 'You Are Here':
                    index = text.rfind('➖')
                    text = text[:index] + "✔" + text[index + 1:] if not index < 0 else text
                else:
                    text += space + ' ' + item + '\n'
            return text

        result = printing(sub_button_list)
        return result if result != '' else 'صفحه اصلی'

    @staticmethod
    def persian_number(text: str):
        text = text.replace('0', '۰')
        text = text.replace('1', '۱')
        text = text.replace('2', '۲')
        text = text.replace('3', '۳')
        text = text.replace('4', '۴')
        text = text.replace('5', '۵')
        text = text.replace('6', '۶')
        text = text.replace('7', '۷')
        text = text.replace('8', '۸')
        text = text.replace('9', '۹')
        return text

    @staticmethod
    def english_number(text: str):
        text = text.replace('۰', '0')
        text = text.replace('۱', '1')
        text = text.replace('۲', '2')
        text = text.replace('۳', '3')
        text = text.replace('۴', '4')
        text = text.replace('۵', '5')
        text = text.replace('۶', '6')
        text = text.replace('۷', '7')
        text = text.replace('۸', '8')
        text = text.replace('۹', '9')
        return text

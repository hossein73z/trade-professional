from kucoin.client import Client
from prettytable import PrettyTable


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

# def persianNumber()

# def englishNumber()

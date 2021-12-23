from colorama import Fore
from telegram import ReplyKeyboardMarkup

from Functions.DatabaseCRUD import update_person, read, raw_buttons_table
from Functions.FormatText import FormatText
from Functions.KeyboardFunctions import get_button_array_array
from Objects.Person import Person
from Objects.RawButton import RawButton


def back_button(person: Person):
    raw_buttons: list[RawButton] = read(table=raw_buttons_table, my_object=RawButton)

    buttons_dict = {}
    if raw_buttons is not None:
        for button in raw_buttons:
            buttons_dict[button.button_id] = button

    try:

        last_button = buttons_dict[buttons_dict[person.person_last_button_id].button_belong_to]

        button_array_array = get_button_array_array(person, last_button.button_id)
        reply_keyboard_markup = ReplyKeyboardMarkup(keyboard=button_array_array,
                                                    resize_keyboard=True,
                                                    one_time_keyboard=False,
                                                    selective=False)

        person.person_last_button_id = last_button.button_id
        update_person(person)

        result = {"mssg": FormatText.button_map(person.person_last_button_id),
                  "reply_keyboard_markup": reply_keyboard_markup}
        return result
    except Exception as e:
        print(Fore.RED + str(e) + Fore.RESET)
        return None

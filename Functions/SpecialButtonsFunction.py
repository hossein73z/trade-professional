from telegram import ReplyKeyboardMarkup

from Functions.KeyboardFunctions import *


def back_button(person: Person, text: str):
    try:
        last_buttons = read(
            table=raw_buttons_table,
            id=read(
                table=raw_buttons_table,
                id=person.person_last_button_id,
                my_object=RawButton)[0].button_belong_to,
            my_object=RawButton)

        last_button = last_buttons[0]
        button_array_array = get_button_array_array(person, last_button.button_id)
        reply_keyboard_markup = ReplyKeyboardMarkup(keyboard=button_array_array,
                                                    resize_keyboard=True,
                                                    one_time_keyboard=False,
                                                    selective=False)

        person.person_last_button_id = last_button.button_id
        update_person(person)

        result = {"mssg": text, "reply_keyboard_markup": reply_keyboard_markup}
        return result
    except Exception as e:
        print(Fore.RED + str(e) + Fore.RESET)
        return None

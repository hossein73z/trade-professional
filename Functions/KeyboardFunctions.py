from telegram import KeyboardButton

from Functions.DatabaseCRUD import *
from Objects.RawButton import RawButton
from Objects.RawSpecialButton import RawSpecialButton


def get_button_array_array(person: Person, button_id):
    raw_buttons: list[RawButton] = read(table=raw_buttons_table, id=button_id, my_object=RawButton)

    if raw_buttons is not None:
        raw_button = raw_buttons[0]
        button_id_array_array = raw_button.button_keyboards
        special_button_id_array_array = raw_button.button_special_keyboards

        button_array_array: list[[KeyboardButton]] = []

        if button_id_array_array is not None:
            for button_id_array in button_id_array_array:
                button_array: list[KeyboardButton] = []
                for button_id in button_id_array:
                    try:
                        temp_button: RawButton = read(table=raw_buttons_table, id=button_id, my_object=RawButton)[0]
                        if temp_button.button_admin_key and person.person_is_admin or not temp_button.button_admin_key:
                            button_array.append(KeyboardButton(text=temp_button.button_text))
                    except Exception as e:
                        print(Fore.RED + str(e) + Fore.RESET)
                        break
                button_array_array.append(button_array)

        if special_button_id_array_array is not None:
            for special_button_id_array in special_button_id_array_array:
                special_button_array = []
                for special_button_id in special_button_id_array:
                    try:
                        temp_button: RawSpecialButton = read(
                            table=raw_special_buttons_table, id=special_button_id, my_object=RawSpecialButton)[0]
                        if temp_button.special_button_admin_key and \
                                person.person_is_admin or not temp_button.special_button_admin_key:
                            special_button_array.append(KeyboardButton(text=temp_button.special_button_text))
                    except Exception as e:
                        print(Fore.RED + str(e) + Fore.RESET)
                        break
                button_array_array.append(special_button_array)
        return button_array_array


def get_pressed_button(person: Person, text: str):
    result = None
    try:
        raw_buttons: list[RawButton] = read(
            table=raw_buttons_table, my_object=RawButton, id=person.person_last_button_id)
        if raw_buttons is not None:
            raw_button = raw_buttons[0]
            button_id_array_array = raw_button.button_keyboards
            for button_id_array in button_id_array_array:
                for button_id in button_id_array:
                    buttons = read(table=raw_buttons_table, my_object=RawButton, id=button_id)
                    if buttons is not None:
                        button = buttons[0]
                        if (button.button_text == text) \
                                and ((raw_button.button_admin_key and person.person_is_admin)
                                     or not raw_button.button_admin_key):
                            result = {'pressed_button': button, 'is_special': False}
                            break

    except Exception as e:
        print(Fore.RED + str(e) + Fore.RESET)

    if result is None:
        try:
            special_button_id_array_array = read(
                table=raw_buttons_table,
                id=person.person_last_button_id,
                my_object=RawButton)[0].button_special_keyboards

            for special_button_id_array in special_button_id_array_array:
                for special_button_id in special_button_id_array:
                    special_button = read(
                        table=raw_special_buttons_table, id=special_button_id, my_object=RawSpecialButton)[0]

                    if (special_button.special_button_text == text) \
                            and ((special_button.special_button_admin_key and person.person_is_admin)
                                 or not special_button.special_button_admin_key):
                        result = {'pressed_button': special_button, 'is_special': True}
                        break

        except Exception as e:
            print(Fore.RED + str(e) + Fore.RESET)
    return result

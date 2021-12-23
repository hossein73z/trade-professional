import json

from colorama import Fore
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext

from Functions.DatabaseCRUD import favorites_table, read, update_person, delete
from Functions.KeyboardFunctions import get_button_array_array
from Functions.SpecialButtonsFunction import back_button
from Objects.Favorite import Favorite
from Objects.Person import Person


def delete_pair_button(person: Person, context: CallbackContext, reply_markup: ReplyKeyboardMarkup):
    favorites: list[Favorite] = read(
        table=favorites_table, my_object=Favorite, person_id=person.person_id)
    if favorites is not None:
        mssg = 'جفت ارزی که قصد حذف آن را دارید انتخاب کنید:\n'
        for favorite in favorites:
            mssg += f'/{favorite.favorite_currency}_{favorite.favorite_base}\n'

        try:
            context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
        except Exception as e:
            print(e)
            context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)
        person.person_progress = json.dumps({'stage': 'DeletePair', 'value': None})
        update_person(person)
    else:
        mssg = "شما هنوز هیچ جفت ارزی را در واچ لیست خود ثبت نکرده اید." \
               "ابتدا با دکمه های زیر حداقل یک ارز را در لیست وارد کنید"
        temp = back_button(person)
        if temp is not None:
            reply_markup = temp['reply_keyboard_markup']
        try:
            context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
        except Exception as e:
            print(e)
            context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)


def delete_pair_confirmation(person: Person, update: Update, context: CallbackContext):
    text = update.effective_message.text
    pair = ""
    is_ok = True

    entities = update.effective_message.entities
    if entities is not None:
        for entity in entities:
            if entity.type == 'bot_command':
                pair = text[entity.offset + 1:entity.length]
                break

        if not pair == "":
            pairs = pair.split('_')
            favorites = read(favorites_table, my_object=Favorite,
                             person_id=person.person_id, currency=pairs[0], base=pairs[1])
            if favorites is not None:
                favorite = favorites[0]

                person.person_progress = json.dumps(
                    {'stage': 'DeletePair_Confirm',
                     'value': {'favorite_id': favorite.favorite_id}})
                update_person(person)

                mssg = 'آیا از حذف جفت ارز ' + f"{favorite.favorite_currency}/{favorite.favorite_base}" + \
                       'اطمینان دارید؟'
                button_array_array = [[KeyboardButton(text='تأیید ✅'), KeyboardButton(text='لغو ❌')]]
                reply_markup = ReplyKeyboardMarkup(
                    button_array_array, resize_keyboard=True, one_time_keyboard=False, selective=False)

                try:
                    context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
                except Exception as e:
                    print(e)
                    context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)

            else:
                is_ok = False
    else:
        is_ok = False

    if not is_ok:
        print(Fore.YELLOW + "Wrong Message" + Fore.RESET)
        mssg = "پیام نامفهوم بود.\nلطفا یکی از گزینه های بالا را انتخاب کنید"

        # Create keyboard to be sent
        button_array_array = get_button_array_array(person, person.person_last_button_id)
        reply_markup = ReplyKeyboardMarkup(
            keyboard=button_array_array, resize_keyboard=True, one_time_keyboard=False, selective=False)

        # Send message
        try:
            context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
        except Exception as e:
            print(e)
            context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)


def delete_pair_confirmed(person: Person, context: CallbackContext):
    reply_markup: ReplyKeyboardMarkup = ReplyKeyboardMarkup([[]])
    # Initialize Progress Stage
    try:
        progress = json.loads(person.person_progress)
    except Exception as e:
        progress = None
        print('Person Progress To JSON Error: ', e)

    favorite: Favorite = \
        read(table=favorites_table, my_object=Favorite, id=progress['value']['favorite_id'])[0]
    delete(favorites_table, id=progress['value']['favorite_id'])
    mssg = f'جفت ارز {favorite.favorite_currency}/{favorite.favorite_base}' \
           f' با موفقیت از لیست شما حذف شد.'

    person.person_progress = ""
    temp = back_button(person)
    if temp is not None:
        reply_markup = temp['reply_keyboard_markup']
    try:
        context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
    except Exception as e:
        print(e)
        context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)

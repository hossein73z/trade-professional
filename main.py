import json
import traceback
import logging

from colorama import Fore
from kucoin.client import Client
from telegram import Message, Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, Dispatcher, CallbackContext
from os import environ

import Functions.AddOrder as AddOrder
import Functions.AddExchange as AddExchange
import Functions.DeletePair as DeletePair
import Functions.AddPair as AddPair
import Functions.KeyboardFunctions as KeyboardFunctions
import Functions.SpecialButtonsFunction as SpecialButtonsFunction
from Functions.DatabaseCRUD import read, initialize_database, add_person, update_person
from Functions.DatabaseCRUD import persons_table, favorites_table, exchanges_table

from Objects.Exchange import Exchange
from Objects.Favorite import Favorite
from Objects.Person import Person
from Objects.RawButton import RawButton
from Functions.FormatText import FormatText

# Initializing variables
logger = logging.getLogger(__name__)
PORT = int(environ.get('PORT', 88))
TOKEN = str(environ.get('bot_token'))
app_name = str(environ.get('app_name', 'trade-professional-bot'))

# creating tables in database and inserting default values
initialize_database()


# Function to be sent to message_handler
def func(update: Update, context: CallbackContext):
    # Extract infos from received update
    user = update.effective_user

    # Check for user existence
    persons = read(table=persons_table, chat_id=update.effective_user.id, my_object=Person)
    # Create user if it is not existed
    if persons is None:
        add_person(Person(None, user.id, user.first_name, user.last_name, user.username, 0, False, 0, 0))
        persons = read(table=persons_table, chat_id=user.id, my_object=Person)
    person: Person = persons[0]

    # Declaring defaults
    mssg = "خطایی در سمت سرور پیش آمده"
    reply_markup = None

    # Create pressed_button object from received text and user level
    pressed_button_dict = KeyboardFunctions.get_pressed_button(person=person, text=update.effective_message.text)

    # Check if received text is a button
    if pressed_button_dict is not None:
        pressed_button: RawButton = pressed_button_dict["pressed_button"]

        # Check if pressed button is special -----------------------------------------------------------------
        if pressed_button_dict["is_special"]:
            pressed_special_button = pressed_button_dict['pressed_button']

            # Back button detected
            if pressed_special_button.special_button_id == 0:
                temp = SpecialButtonsFunction.back_button(person)
                if temp is not None:
                    mssg = temp['mssg']
                    reply_markup = temp['reply_keyboard_markup']
                try:
                    context.bot.sendMessage(chat_id=user.id, text=mssg, reply_markup=reply_markup)
                except Exception as e:
                    print(traceback.format_exc(), e)
                    context.bot.sendMessage(chat_id=user.id, text=str(e), reply_markup=reply_markup)

            # Cancel button detected
            elif pressed_special_button.special_button_id == 1:
                person.person_progress = ''
                mssg = 'عملیات لغو شد'
                try:
                    context.bot.sendMessage(chat_id=user.id, text=mssg, reply_markup=reply_markup)
                except Exception as e:
                    print(traceback.format_exc(), e)
                    context.bot.sendMessage(chat_id=user.id, text=str(e), reply_markup=reply_markup)
                temp = SpecialButtonsFunction.back_button(person)
                if temp is not None:
                    mssg = temp['mssg']
                    reply_markup = temp['reply_keyboard_markup']
                try:
                    context.bot.sendMessage(chat_id=user.id, text=mssg, reply_markup=reply_markup)
                except Exception as e:
                    print(traceback.format_exc(), e)
                    context.bot.sendMessage(chat_id=user.id, text=str(e), reply_markup=reply_markup)

            # Prices button detected
            elif pressed_special_button.special_button_id == 2:
                # Get list of person favorites
                favorites: list[Favorite] = read(
                    table=favorites_table, my_object=Favorite, person_id=person.person_id)
                exchanges: list[Exchange] = read(
                    table=exchanges_table, my_object=Exchange, person_id=person.person_id, name='KuCoin')

                # Chek if user has registered exchange
                if exchanges is not None:

                    # Send Waiting Message
                    try:
                        message: Message = context.bot.sendMessage(chat_id=user.id, text='در حال دریافت اطلاعات')
                    except Exception as e:
                        print(traceback.format_exc(), e)
                        message: Message = context.bot.sendMessage(chat_id=user.id, text=str(e))

                    # Create table from user favorites
                    if favorites is not None:
                        # Read exchange
                        exchange: Exchange = exchanges[0]
                        client = Client(
                            api_key=exchange.api_key,
                            api_secret=exchange.api_secret,
                            passphrase=exchange.api_passphrase,
                            sandbox=exchange.api_sandbox)

                        mssg = FormatText.create_table_for_pairs(
                            client, ['Pair', 'Price'], favorites, {'Price': 'l'})
                        mssg = f"`{mssg}`"

                        # Edit message to table
                        try:
                            context.bot.edit_message_text(
                                text=mssg, chat_id=user.id, message_id=message.message_id, parse_mode='Markdown')
                        except Exception as e:
                            print(traceback.format_exc(), e)
                            context.bot.edit_message_text(
                                text=str(e), chat_id=user.id, message_id=message.message_id)
                    else:
                        mssg = "هیچ ارزی در واچ لیست شما ثبت نشده. از دکمه های زیر برای ثبت ارز در واچلیست استفاده کنید"
                        try:
                            context.bot.edit_message_text(
                                text=mssg, chat_id=user.id, message_id=message.message_id, parse_mode='Markdown')
                        except Exception as e:
                            print(traceback.format_exc(), e)
                            context.bot.edit_message_text(
                                text=str(e), chat_id=user.id, message_id=message.message_id, parse_mode='Markdown')

                # Send error if user has no exchange registered
                else:
                    mssg = 'شما هنوز هیچ صرافی ای ثبت نکرده اید. ' \
                           'برای این کار به صفحه اصلی برگشته و از قسمت تنظیمات وارد بخش صرافی ها شوید'
                    try:
                        context.bot.sendMessage(chat_id=user.id, text=mssg)
                    except Exception as e:
                        print(traceback.format_exc(), e)
                        context.bot.sendMessage(chat_id=user.id, text=str(e))

        # Handle non_special buttons--------------------------------------------------------------------------
        else:
            # Echo the received message
            mssg = FormatText.button_map(pressed_button.button_id)
            # Create keyboard to be sent
            button_array_array: list[[KeyboardButton]] = KeyboardFunctions.get_button_array_array(
                person, pressed_button.button_id)
            reply_markup = ReplyKeyboardMarkup(
                keyboard=button_array_array, resize_keyboard=True, one_time_keyboard=False, selective=False)

            # Change user last_button_id to next level
            person.person_last_button_id = pressed_button.button_id
            # Upgrade user with new last_button_id
            update_person(person)

            try:
                context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
            except Exception as e:
                print(traceback.format_exc(), e)
                context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)

            # Add Pair Button Pressed
            if pressed_button.button_id == 5:
                AddPair.add_pair_button(person, context=context, reply_markup=reply_markup)

            # Delete Pair Button Pressed
            elif pressed_button.button_id == 6:
                DeletePair.delete_pair_button(person=person, context=context, reply_markup=reply_markup)

            # Exchange Button Pressed
            elif pressed_button.button_id == 7:
                AddExchange.exchange_button(person=person, context=context, reply_markup=reply_markup)

            # Add Exchange Button Pressed
            elif pressed_button.button_id == 11:
                AddExchange.add_exchange_button(person=person, context=context)

            # Orders Button Pressed
            elif pressed_button.button_id == 13:
                exchanges: list[Exchange] = read(
                    table=exchanges_table, my_object=Exchange, person_id=person.person_id)

                # Chek if user has registered exchange
                if exchanges is not None:
                    pass

                # Send error if user has no exchange registered
                else:
                    mssg = 'شما هنوز هیچ صرافی ای ثبت نکرده اید. ' \
                           'برای این کار به صفحه اصلی برگشته و از قسمت تنظیمات وارد بخش صرافی ها شوید'
                    temp = SpecialButtonsFunction.back_button(person)
                    if temp is not None:
                        mssg = temp['mssg']
                        reply_markup = temp['reply_keyboard_markup']
                    try:
                        context.bot.sendMessage(chat_id=user.id, text=mssg, reply_markup=reply_markup)
                    except Exception as e:
                        print(traceback.format_exc(), e)
                        context.bot.sendMessage(chat_id=user.id, text=str(e), reply_markup=reply_markup)

            # Add Order Button Pressed
            elif pressed_button.button_id == 14:
                AddOrder.add_order_button(person=person, context=context, reply_markup=reply_markup)

    # Handle Non_Button Texts---------------------------------------------------------------------------------
    else:

        # Initialize Progress Stage
        try:
            progress = json.loads(person.person_progress)
        except Exception as e:
            progress = None
            print('Person Progress To JSON Error: ', e)

        # Check person last pressed button
        if person.person_last_button_id == 5:
            # Check user stage
            if progress['stage'] == 'AddPair_exchange':
                AddPair.add_pair_exchange(person=person, context=context, update=update)
            # Check user stage
            if progress['stage'] == 'AddPair':
                AddPair.add_pair_confirmation(person=person, update=update, context=context)
            # Check user stage
            elif progress['stage'] == 'AddPair_Confirm':
                # User confirms to add new pair
                if update.effective_message.text == 'تأیید ✅':
                    AddPair.add_pair_confirmed(person=person, context=context)
                # User sent new base currency
                else:
                    AddPair.add_base(person=person, update=update, context=context)

        # Check person last pressed button
        elif person.person_last_button_id == 6:
            if progress['stage'] == 'DeletePair':
                DeletePair.delete_pair_confirmation(person=person, update=update, context=context)
            elif progress['stage'] == 'DeletePair_Confirm':
                # User confirms to delete the pair
                if update.effective_message.text == 'تأیید ✅':
                    DeletePair.delete_pair_confirmed(person=person, context=context)

        # Check person last pressed button
        elif person.person_last_button_id == 11:
            if progress['stage'] == 'AddExchange_Name':
                AddExchange.add_exchange_name(person, update, context)
            elif progress['stage'] == 'AddExchange_API':
                if progress['value']['exchange'] == 'KuCoin':
                    AddExchange.add_exchange_kucoin(person, update, context)

        elif person.person_last_button_id == 14:
            if progress['stage'] == 'AddOrder_exchange':
                AddOrder.add_order_exchange(person, update, context)
            elif progress['stage'] == 'AddOrder_currency':
                AddOrder.add_order_currency(person, update, context)
            elif progress['stage'] == 'AddOrder_pair':
                AddOrder.add_order_pair(person=person,
                                        context=context) if update.effective_message.text == 'تأیید ✅' else AddOrder.add_order_base(
                    person, update, context)
            elif progress['stage'] == 'AddOrder_side':
                AddOrder.add_order_side(person, update, context)
            elif progress['stage'] == 'AddOrder_type':
                AddOrder.add_order_type(person, update, context)
            elif progress['stage'] == 'AddOrder_price':
                AddOrder.add_order_price(person, update, context)
            elif progress['stage'] == 'AddOrder_value':
                AddOrder.add_order_value(person, update, context)

        # Most default reaction for texts which is a simple error
        else:
            print(Fore.YELLOW + "Wrong Message" + Fore.RESET)
            mssg = "پیام نامفهوم بود.\nلطفا یکی از گزینه های زیر را انتخاب کنید"

            # Create keyboard to be sent
            button_array_array = KeyboardFunctions.get_button_array_array(person, person.person_last_button_id)
            reply_markup = ReplyKeyboardMarkup(
                keyboard=button_array_array, resize_keyboard=True, one_time_keyboard=False, selective=False)

            # Send message
            try:
                context.bot.sendMessage(chat_id=user.id, text=mssg, reply_markup=reply_markup)
            except Exception as e:
                print(traceback.format_exc(), e)
                context.bot.sendMessage(chat_id=user.id, text=str(e), reply_markup=reply_markup)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    updater = Updater(TOKEN, use_context=True)
    dp: Dispatcher = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text, func, run_async=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN,
                          webhook_url=f'https://{app_name}.herokuapp.com/' + TOKEN)
    # updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

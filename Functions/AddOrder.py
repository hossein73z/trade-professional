import json

from kucoin.client import Client
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update, ReplyKeyboardRemove
from telegram.ext import CallbackContext

from Functions.DatabaseCRUD import read, exchanges_table, update_person
from Functions.KeyboardFunctions import get_button_array_array
from Functions.SpecialButtonsFunction import back_button
from Objects.Exchange import Exchange
from Objects.Person import Person


def add_order_button(person: Person, context: CallbackContext, reply_markup: ReplyKeyboardMarkup):
    exchanges: list[Exchange] = read(table=exchanges_table, my_object=Exchange, person_id=person.person_id)
    if exchanges is not None:
        # Change person progress to ((AddOrder_exchange)) stage
        person.person_progress = json.dumps({'stage': 'AddOrder_exchange', 'value': None})
        update_person(person)

        button_array_array = reply_markup.keyboard
        for exchange in exchanges:
            text = exchange.name
            if exchange.name == 'KuCoin':
                text = 'کوکوین (KuCoin)'
            button_array_array.insert(0, [KeyboardButton(text=text)])
        reply_markup = ReplyKeyboardMarkup(
            button_array_array, resize_keyboard=True, one_time_keyboard=False, selective=False)
        mssg = 'لطفا صرافی مد نظر خود را از دکمه های پایین انتخاب کنید.'
        try:
            context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
        except Exception as e:
            print(e)
            context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)

        pass
    else:
        mssg = 'شما هنوز هیچ صرافی ای ثبت نکرده اید. ' \
               'برای این کار به صفحه اصلی برگشته و از قسمت تنظیمات وارد بخش صرافی ها شوید'
        reply_markup = None
        temp = back_button(person)
        if temp is not None:
            reply_markup = temp['reply_keyboard_markup']
        try:
            context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
        except Exception as e:
            print(e)
            context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)


def add_order_exchange(person: Person, update: Update, context: CallbackContext):
    # Create keyboard to be sent
    button_array_array: list[[KeyboardButton]] = get_button_array_array(person, person.person_last_button_id)
    reply_markup = ReplyKeyboardMarkup(
        keyboard=button_array_array, resize_keyboard=True, one_time_keyboard=False, selective=False)

    name = "Nothing"
    if update.effective_message.text == 'کوکوین (KuCoin)':
        name = 'KuCoin'
    exchanges = read(table=exchanges_table, my_object=Exchange, person_id=person.person_id, name=name)

    if exchanges is not None:
        # Request user to send crypto symbol
        mssg = 'نماد ارز مد نظر خود را ارسال کنید.مثال: ETH'
        try:
            context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
        except Exception as e:
            print(e)
            context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)

        # Change person progress to ((AddOrder)) stage
        person.person_progress = json.dumps({'stage': 'AddOrder', 'value': None})
        update_person(person)
    else:
        mssg = 'صرافی مد نظر شما یافت نشد'
        button_array_array = reply_markup.keyboard
        exchanges: list[Exchange] = read(table=exchanges_table, my_object=Exchange, person_id=person.person_id)
        for exchange in exchanges:
            text = exchange.name
            if exchange.name == 'KuCoin':
                text = 'کوکوین (KuCoin)'
            button_array_array.insert(0, [KeyboardButton(text=text)])
        reply_markup = ReplyKeyboardMarkup(
            button_array_array, resize_keyboard=True, one_time_keyboard=False, selective=False)
        try:
            context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
        except Exception as e:
            print(e)
            context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)


def add_pair_confirmation(person: Person, update: Update, context: CallbackContext):
    # Initialize Progress Stage
    try:
        progress = json.loads(person.person_progress)
    except Exception as e:
        progress = None
        print('Person Progress To JSON Error: ', e)

    exchanges = read(
        table=exchanges_table, my_object=Exchange, person_id=person.person_id, name=progress['value']['exchange'])
    if exchanges is not None:
        # Extract currency symbol from user text
        text = update.effective_message.text
        text = text.replace(" ", "")
        text = text.upper()

        # Create ReplyMarkup
        reply_markup = ReplyKeyboardRemove()
        mssg = 'در حال دریافت اطلاعات از سرور کوکوین. لطفا منتظر بمانید'
        try:
            message = context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
        except Exception as e:
            print(e)
            message = context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)

        # Read exchange
        exchange: Exchange = exchanges[0]
        client = Client(
            api_key=exchange.api_key,
            api_secret=exchange.api_secret,
            passphrase=exchange.api_passphrase,
            sandbox=exchange.api_sandbox)
        ticker = client.get_ticker(f'{text}-USDT')

        # Check if the symbol exists on the exchange
        if ticker is not None:

            # Update user progress to new stage and with value
            person.person_progress = json.dumps(
                {'stage': 'AddOrder_Confirm', 'value': {'currency': text, 'base': 'USDT'}})
            update_person(person)

            # Prepare confirmation message to user
            mssg = f'جفت ارز {text}/USDT در صرافی کوکوین یافت شد. قیمت حال حاضر برابر {ticker["price"]}' \
                   f' میباشد. درصورت موافقت برای ثبت این جفت ارز، دکمه ((تأیید ✅)) را فشار دهید.\n' \
                   f'همچنین میتوانید درصورت تمایل برای تغییر ارز پایه از تتر به ارزی دیگر، ' \
                   f'نماد ارز مربوطه را همینجا ارسال کنید.'

            # delete formerly sent message
            context.bot.deleteMessage(chat_id=person.person_chat_id, message_id=message.message_id)

            # Send confirmation message to user
            button_array_array = [[KeyboardButton(text='تأیید ✅'), KeyboardButton(text='لغو ❌')]]
            reply_markup = ReplyKeyboardMarkup(
                button_array_array, resize_keyboard=True, one_time_keyboard=False, selective=False)
            try:

                context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
            except Exception as e:
                print(e)
                context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)
        else:
            # Update user progress to new stage and with value
            person.person_progress = json.dumps(
                {'stage': 'AddPair_Confirm', 'value': None})
            update_person(person)

            button_array_array = get_button_array_array(person, person.person_last_button_id)
            reply_markup = ReplyKeyboardMarkup(
                button_array_array, resize_keyboard=True, one_time_keyboard=False, selective=False)
            mssg = 'نماد مورد نظر در صرافی کوکوین یافت نشد. لطفا دوباره امتحان کنید.'
            try:
                context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
                context.bot.deleteMessage(chat_id=person.person_chat_id, message_id=message.message_id)
            except Exception as e:
                print(e)
                context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)
    else:
        mssg = 'شما هوز صرافی ثبت نکرده اید'
        reply_markup = None
        temp = back_button(person)
        if temp is not None:
            reply_markup = temp['reply_keyboard_markup']
        try:
            context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
        except Exception as e:
            print(e)
            context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)

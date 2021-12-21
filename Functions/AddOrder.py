import json

from kucoin.client import Client
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update, ReplyKeyboardRemove, Message
from telegram.ext import CallbackContext

from Functions.DatabaseCRUD import read, exchanges_table, update_person
from Functions.FormatText import FormatText
from Functions.KeyboardFunctions import get_button_array_array
from Functions.SpecialButtonsFunction import back_button
from Objects.Exchange import Exchange
from Objects.Person import Person


def add_order_button(person: Person, context: CallbackContext, reply_markup: ReplyKeyboardMarkup):
    exchanges: list[Exchange] = read(table=exchanges_table, my_object=Exchange, person_id=person.person_id)
    if exchanges is not None:
        # Change person progress to ((AddOrder_exchange)) stage
        person.person_progress = json.dumps({'stage': 'AddOrder_exchange', 'value': {}})
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
    # Initialize Progress Stage
    try:
        progress: dict = json.loads(person.person_progress)
    except Exception as e:
        progress = {}
        print('Person Progress To JSON Error: ', e)

    # Create keyboard to be sent
    button_array_array: list[[KeyboardButton]] = get_button_array_array(person, person.person_last_button_id)
    reply_markup = ReplyKeyboardMarkup(
        keyboard=button_array_array, resize_keyboard=True, one_time_keyboard=False, selective=False)

    name = "Nothing"
    text = update.effective_message.text
    text_lower = text.replace(" ", "")
    text_lower = text_lower.lower()
    if text == 'کوکوین (KuCoin)' or text_lower == 'کوکوین' or text_lower == 'کوکین' or text_lower == 'kucoin':
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
        progress['stage'] = 'AddOrder_currency'
        progress['value']['exchange'] = name
        person.person_progress = json.dumps(progress)
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


def add_order_currency(person: Person, update: Update, context: CallbackContext):
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

        # Create keyboard to be sent
        button_array_array: list[[KeyboardButton]] = get_button_array_array(person, person.person_last_button_id)
        reply_markup = ReplyKeyboardMarkup(
            keyboard=button_array_array, resize_keyboard=True, one_time_keyboard=False, selective=False)
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
            progress['stage'] = 'AddOrder_pair'
            progress['value']['currency'] = text
            progress['value']['base'] = 'USDT'
            person.person_progress = json.dumps(progress)
            update_person(person)

            # Prepare confirmation message to user
            mssg = f'جفت ارز {text}/USDT در صرافی کوکوین یافت شد. قیمت حال حاضر برابر {ticker["price"]}' \
                   f' میباشد. درصورت موافقت، دکمه ((تأیید ✅)) را فشار دهید.\n' \
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


def add_order_base(person: Person, update: Update, context: CallbackContext):
    # Initialize Progress Stage
    try:
        progress = json.loads(person.person_progress)
    except Exception as e:
        progress = None
        print('Person Progress To JSON Error: ', e)

    # Send user the waiting message
    mssg = 'در حال دریافت اطلاعات از سرور کوکوین. لطفا منتظر بمانید'
    try:
        message = context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg)
    except Exception as e:
        print(e)
        message = context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e))

    exchanges = read(
        table=exchanges_table, my_object=Exchange, person_id=person.person_id, name=progress['value']['exchange'])
    if exchanges is not None:
        exchange: Exchange = exchanges[0]
        client = Client(
            api_key=exchange.api_key,
            api_secret=exchange.api_secret,
            passphrase=exchange.api_passphrase,
            sandbox=exchange.api_sandbox)

        # Extract currency symbol from user text
        text = update.effective_message.text
        text = text.replace(" ", "")
        text = text.upper()
        ticker = client.get_ticker(f"{progress['value']['currency']}-{text}")

        # Check if the symbol exists on the exchange
        if ticker is not None:

            # Prepare confirmation message to user
            mssg = f'جفت ارز {progress["value"]["currency"]}/{text}' \
                   f' در صرافی کوکوین یافت شد. قیمت حال حاضر برابر {ticker["price"]}' \
                   f' میباشد. درصورت موافقت، دکمه ((تأیید ✅)) را فشار دهید.\n' \
                   f'همچنین میتوانید درصورت تمایل برای تغییر ارز پایه به ارزی دیگر، ' \
                   f'نماد ارز مربوطه را همینجا ارسال کنید.'
            button_array_array = [[KeyboardButton(text='تأیید ✅'), KeyboardButton(text='لغو ❌')]]
            reply_markup = ReplyKeyboardMarkup(
                button_array_array, resize_keyboard=True, one_time_keyboard=False, selective=False)

            # Update user progress to new stage and with value
            progress['stage'] = 'AddOrder_pair'
            progress['value']['base'] = text
            person.person_progress = json.dumps(progress)
            update_person(person)

            # delete formerly sent message
            context.bot.deleteMessage(chat_id=person.person_chat_id, message_id=message.message_id)

            # Send confirmation message to user
            try:
                context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
            except Exception as e:
                print(e)
                context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)

        else:
            context.bot.deleteMessage(chat_id=person.person_chat_id, message_id=message.message_id)

            button_array_array = get_button_array_array(person, person.person_last_button_id)
            reply_markup = ReplyKeyboardMarkup(
                button_array_array, resize_keyboard=True, one_time_keyboard=False, selective=False)
            mssg = 'جفت ارز مورد نظر در صرافی کوکوین یافت نشد. لطفا ارز پایه ی دیگری را امتحان کنید.'
            try:
                context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
            except Exception as e:
                print(e)
                context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)


def add_order_pair(person: Person, context: CallbackContext):
    # Initialize Progress Stage
    try:
        progress = json.loads(person.person_progress)
    except Exception as e:
        progress = None
        print('Person Progress To JSON Error: ', e)

    progress['stage'] = 'AddOrder_side'
    person.person_progress = json.dumps(progress)
    update_person(person)

    mssg = 'قصد ثبت سفارش خرید دارید یا فروش؟'
    button_array_array: list[[KeyboardButton]] = get_button_array_array(person, person.person_last_button_id)
    button_array_array.insert(0, [KeyboardButton(text='خرید'), KeyboardButton(text='فروش')])
    reply_markup = ReplyKeyboardMarkup(
        keyboard=button_array_array, resize_keyboard=True, one_time_keyboard=False, selective=False)
    try:
        context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
    except Exception as e:
        print(e)
        context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)


def add_order_side(person: Person, update: Update, context: CallbackContext):
    # Initialize Progress Stage
    try:
        progress = json.loads(person.person_progress)
    except Exception as e:
        progress = None
        print('Person Progress To JSON Error: ', e)

    if update.effective_message.text == 'خرید' or update.effective_message.text == 'فروش':
        if update.effective_message.text == 'خرید':
            progress['value']['side'] = Client.SIDE_BUY
        elif update.effective_message.text == 'فروش':
            progress['value']['side'] = Client.SIDE_SELL

        progress['stage'] = 'AddOrder_type'
        person.person_progress = json.dumps(progress)
        update_person(person)

        mssg = 'لطفا نوع سفارش خود را مشخص کنید؟'
        # Create keyboard to be sent
        button_array_array: list[[KeyboardButton]] = get_button_array_array(person, person.person_last_button_id)
        button_array_array.insert(0, [KeyboardButton(text='بازار'), KeyboardButton(text='محدود')])
        reply_markup = ReplyKeyboardMarkup(
            keyboard=button_array_array, resize_keyboard=True, one_time_keyboard=False, selective=False)
        try:
            context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
        except Exception as e:
            print(e)
            context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)

    else:
        mssg = 'پیام مفهوم نبود. لطفا یکی از گیزنه های زیر را انتخاب کنید'
        button_array_array: list[[KeyboardButton]] = get_button_array_array(person, person.person_last_button_id)
        button_array_array.insert(0, [KeyboardButton(text='خرید'), KeyboardButton(text='فروش')])
        reply_markup = ReplyKeyboardMarkup(
            keyboard=button_array_array, resize_keyboard=True, one_time_keyboard=False, selective=False)
        try:
            context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
        except Exception as e:
            print(e)
            context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)


def add_order_type(person: Person, update: Update, context: CallbackContext):
    # Initialize Progress Stage
    try:
        progress = json.loads(person.person_progress)
    except Exception as e:
        progress = None
        print('Person Progress To JSON Error: ', e)

    if update.effective_message.text == 'بازار' or update.effective_message.text == 'محدود':
        if update.effective_message.text == 'محدود':

            progress['stage'] = 'AddOrder_price'
            progress['value']['type'] = Client.ORDER_LIMIT
            person.person_progress = json.dumps(progress)
            update_person(person)

            mssg = 'در چه قیمتی میخواهید سفارش را قرار دهید؟ '
            # Create keyboard to be sent
            button_array_array = get_button_array_array(person, person.person_last_button_id)
            reply_markup = ReplyKeyboardMarkup(
                keyboard=button_array_array, resize_keyboard=True, one_time_keyboard=False, selective=False)
            try:
                context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
            except Exception as e:
                print(e)
                context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)

        elif update.effective_message.text == 'بازار':
            progress['value']['type'] = Client.ORDER_MARKET
            # progress['stage'] = 'AddOrder_value'

    else:
        mssg = 'پیام مفهوم نبود. لطفا یکی از گیزنه های زیر را انتخاب کنید'
        button_array_array: list[[KeyboardButton]] = get_button_array_array(person, person.person_last_button_id)
        button_array_array.insert(0, [KeyboardButton(text='بازار'), KeyboardButton(text='محدود')])
        reply_markup = ReplyKeyboardMarkup(
            keyboard=button_array_array, resize_keyboard=True, one_time_keyboard=False, selective=False)
        try:
            context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
        except Exception as e:
            print(e)
            context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)


def add_order_price(person: Person, update: Update, context: CallbackContext):
    # Initialize Progress Stage
    try:
        progress = json.loads(person.person_progress)
    except Exception as e:
        progress = None
        print('Person Progress To JSON Error: ', e)

    text = update.effective_message.text
    text = text.replace(" ", "")
    text = FormatText.english_number(text=text)

    price = 0
    try:
        price = float(text)
    except Exception as e:
        print(e)

    if price > 0:
        progress['stage'] = 'AddOrder_value'
        progress['value']['price'] = price
        person.person_progress = json.dumps(progress)
        update_person(person)
        currency = progress['value']['currency']
        base = progress['value']['base']

        if progress['value']['side'] == Client.SIDE_SELL:
            mssg = 'چه مقدار %s میخواهید بفروشید؟ ' \
                   'لطفا مقدار %s را برای فروش ارسال کنید. ' \
                   'دقت کنید که مقدار خود ارزی که میخواهید بفروشید را ارسال کنید، ' \
                   'نه مقدار دلار یا ارز پایه. برای مثال برای فروش 0.2 %s در قیمت وارد شده که معادل %s %s میشود، ' \
                   'تنها عدد 0.2 را ارسال کنید' \
                   % (currency, currency, currency, str(price * 0.2), base)

        elif progress['value']['side'] == Client.SIDE_BUY:
            mssg = 'به چه اندازه %s میخواهید بخرید؟ ' \
                   'لطفا مقدار %s را برای خرید ارسال کنید. ' \
                   'دقت کنید که مقدار ارز پایه را برای خرید وارد کنید، ' \
                   'نه مقدار %s. برای مثال برای خرید 0.2 %s که معادل %s %s میشود، تنها عدد %s را وارد کنید ' \
                   % (currency, base, currency, currency, str(price * 0.2), base, str(price * 0.2))
        else:
            mssg = 'خطای ناشناخته پیش آمده. لطافا کلید لغو را زده و از ابتدا شروع کنید'

        # Create keyboard to be sent
        button_array_array = get_button_array_array(person, person.person_last_button_id)
        reply_markup = ReplyKeyboardMarkup(
            keyboard=button_array_array, resize_keyboard=True, one_time_keyboard=False, selective=False)
        try:
            context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
        except Exception as e:
            print(e)
            context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)

    else:
        mssg = "مبلغ وارد شده صحیح نیست. لطفا فقط عدد ارسال کنید"
        # Create keyboard to be sent
        button_array_array = get_button_array_array(person, person.person_last_button_id)
        reply_markup = ReplyKeyboardMarkup(
            keyboard=button_array_array, resize_keyboard=True, one_time_keyboard=False, selective=False)
        try:
            context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
        except Exception as e:
            print(e)
            context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)


def add_order_value(person: Person, update: Update, context: CallbackContext):
    # Initialize Progress Stage
    try:
        progress = json.loads(person.person_progress)
    except Exception as e:
        progress = None
        print('Person Progress To JSON Error: ', e)

    text = update.effective_message.text
    text = text.replace(" ", "")
    text = FormatText.english_number(text=text)

    value = 0.0
    try:
        value = float(text)
    except Exception as e:
        print(e)

    if value > 0:
        progress['stage'] = 'AddOrder_confirmation'
        progress['value']['value'] = value
        person.person_progress = json.dumps(progress)
        update_person(person)
        currency = progress['value']['currency']
        base = progress['value']['base']
        price = progress['value']['price']
        exchanges: list[Exchange] = read(
            table=exchanges_table, my_object=Exchange, person_id=person.person_id, name=progress['value']['exchange'])
        exchange = exchanges[0]
        client = Client(
            api_key=exchange.api_key,
            api_secret=exchange.api_secret,
            passphrase=exchange.api_passphrase,
            sandbox=exchange.api_sandbox)
        ticker = client.get_ticker(f'{currency}-{base}')
        accounts_currency = client.get_accounts(currency=currency)
        accounts_base = client.get_accounts(currency=base)
        market_percent = round(abs(float(ticker['price']) - price) * 100 / float(ticker['price']), 2)
        value_amount = 0.0
        amount = round(value * price, 8)
        up_or_down = 'پایین تر' if float(ticker['price']) - price > 0 else 'بالاتر'
        order_side = ''
        value_name = ''
        amount_name = ''

        if progress['value']['side'] == Client.SIDE_SELL:
            order_side = 'فروش'
            value_name = currency
            amount_name = base
            for account in accounts_currency:
                value_amount += float(account['balance'])

        elif progress['value']['side'] == Client.SIDE_BUY:
            order_side = 'خرید'
            value_name = base
            amount_name = currency
            for account in accounts_base:
                value_amount += float(account['balance'])

        order_type = 'بازار' if progress['value']['type'] == Client.ORDER_MARKET else 'محدود'
        portfolio_percent = round(
            (value /
             value_amount)
            * 100,
            2)

        mssg = f"*خلاصه سفارش:*" + '\n' + \
               f"*   نوع سفارش: *{order_side} {order_type}" + '\n' + \
               f"*   صرافی: *{exchange.name}" + '\n' + \
               f"*   جفت ارز: *{currency + '/' + base}" + '\n' + \
               f"*   قیمت: *{str(price)}" + '\n' + \
               f"*   مقدار: *{str(value)} {value_name}" + '\n' + \
               f"ـ------------------------------" + '\n' + \
               f"قیمت لحظه ای این جفت ارز برابر {str(ticker['price'])} میباشد." + '\n' + \
               f"شما قصد دارید در {str(market_percent)} درصد {up_or_down} از قیمت بازار سفارش را قرار دهید." + '\n' + \
               f"در این سفارش {str(portfolio_percent)}  درصد کل {value_name} های شما " + \
               f"به ارزش {str(amount)} {amount_name} قرار خواهند گرفت." + '\n' + '\n' + \
               f"در صورت تاییدو لطفا کلید تایید را فشار دهید"

        # Create keyboard to be sent
        button_array_array = [[KeyboardButton(text='تأیید ✅'), KeyboardButton(text='لغو ❌')]]
        reply_markup = ReplyKeyboardMarkup(
            button_array_array, resize_keyboard=True, one_time_keyboard=False, selective=False)
        try:
            context.bot.sendMessage(
                chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup, parse_mode='Markdown')
        except Exception as e:
            print(e)
            context.bot.sendMessage(
                chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup, parse_mode='Markdown')

    else:
        mssg = "مقدار وارد شده صحیح نیست. لطفا فقط عدد ارسال کنید"
        # Create keyboard to be sent
        button_array_array = get_button_array_array(person, person.person_last_button_id)
        reply_markup = ReplyKeyboardMarkup(
            keyboard=button_array_array, resize_keyboard=True, one_time_keyboard=False, selective=False)
        try:
            context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
        except Exception as e:
            print(e)
            context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)

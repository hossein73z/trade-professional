from kucoin.client import Client
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, KeyboardButton
from telegram.ext import CallbackContext

from Functions.FormatText import FormatText
from Functions.DatabaseCRUD import *
from Functions.SpecialButtonsFunction import back_button
from Objects.Exchange import Exchange
from Objects.Person import Person


def add_pair_button(person: Person, context: CallbackContext, reply_markup: ReplyKeyboardMarkup):
    exchanges = read(table=exchanges_table, my_object=Exchange, person_id=person.person_id, name='KuCoin')
    if exchanges is not None:
        # Request user to send crypto symbol
        mssg = 'نماد ارز مد نظر خود را ارسال کنید.مثال: ETH'
        try:
            context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
        except Exception as e:
            print(e)
            context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)

        # Change person progress to ((AddPair)) stage
        person.person_progress = json.dumps({'stage': 'AddPair', 'value': None})
        update_person(person)
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


def add_pair_confirmation(person: Person, update: Update, context: CallbackContext):
    exchanges = read(table=exchanges_table, my_object=Exchange, person_id=person.person_id, name='KuCoin')
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
                {'stage': 'AddPair_Confirm', 'value': {'currency': text, 'base': 'USDT'}})
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

            button_array_array = [[KeyboardButton(text='لغو ❌')]]
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


def add_pair_confirmed(person: Person, context: CallbackContext):
    reply_markup: ReplyKeyboardMarkup = ReplyKeyboardMarkup([[]])
    # Initialize Progress Stage
    try:
        progress = json.loads(person.person_progress)
    except Exception as e:
        progress = None
        print('Person Progress To JSON Error: ', e)

    # Read user favorites
    favorites = read(table=favorites_table, my_object=Favorite,
                     person_id=person.person_id, currency=progress['value']['currency'], base=progress['value']['base'])

    exchanges = read(table=exchanges_table, my_object=Exchange, person_id=person.person_id, name='KuCoin')
    if exchanges is not None:
        exchange: Exchange = exchanges[0]
        client = Client(
            api_key=exchange.api_key,
            api_secret=exchange.api_secret,
            passphrase=exchange.api_passphrase,
            sandbox=exchange.api_sandbox)
        ticker = client.get_ticker(f"{progress['value']['currency']}-{progress['value']['base']}")

        if ticker is not None:
            # The pair does not exist in user watchlist
            if favorites is None:
                add_favorite(Favorite(None,
                                      person.person_id,
                                      exchange.id,
                                      progress['value']['currency'],
                                      progress['value']['base']))

                mssg = f"جفت ارز {progress['value']['currency']}/{progress['value']['base']}" \
                       f" با موفقیت در واچ لیست شما قرار گرفت.\n"
                person.person_progress = json.dumps("")
                temp = back_button(person)
                if temp is not None:
                    reply_markup = temp['reply_keyboard_markup']
                try:
                    context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
                except Exception as e:
                    print(e)
                    context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)

                mssg = "لطفا چند لحظه صبر کنید..."
                try:
                    message = context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg)
                except Exception as e:
                    print(e)
                    message = context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e))

                favorites = read(
                    table=favorites_table, my_object=Favorite, person_id=person.person_id)

                mssg = FormatText.create_table_for_pairs(
                    client, ['Pair', 'Price'], favorites,
                    {'Price': 'l'}).get_string() if favorites is not None else 'خطایی در دریافت اطلاعات پیش آمده'
                mssg = f'`{mssg}`'

                try:
                    context.bot.edit_message_text(
                        chat_id=person.person_chat_id, text=mssg, message_id=message.message_id, parse_mode='Markdown')
                except Exception as e:
                    print(e)
                    context.bot.edit_message_text(
                        chat_id=person.person_chat_id, text=str(e), message_id=message.message_id,
                        parse_mode='Markdown')

            # The requested pair is already in user watchlist
            else:
                mssg = f"جفت ارز {progress['value']['currency']}/{progress['value']['base']}" \
                       f" از قبل در واچلیست شما قرار دارد"
                temp = back_button(person)
                if temp is not None:
                    reply_markup = temp['reply_keyboard_markup']
                try:
                    context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
                except Exception as e:
                    print(e)
                    context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)
    else:
        mssg = 'شما هوز صرافی ثبت نکرده اید'
        temp = back_button(person)
        if temp is not None:
            reply_markup = temp['reply_keyboard_markup']
        try:
            context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
        except Exception as e:
            print(e)
            context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)


def add_base(person: Person, update: Update, context: CallbackContext):
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

    exchanges = read(table=exchanges_table, my_object=Exchange, person_id=person.person_id, name='KuCoin')
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
        progress['value']['base'] = text
        ticker = client.get_ticker(f"{progress['value']['currency']}-{progress['value']['base']}")

        # Check if the symbol exists on the exchange
        if ticker is not None:

            # Prepare confirmation message to user
            mssg = f'جفت ارز {progress["value"]["currency"]}/{progress["value"]["base"]}' \
                   f' در صرافی کوکوین یافت شد. قیمت حال حاضر برابر {ticker["price"]}' \
                   f' میباشد. درصورت موافقت برای ثبت این جفت ارز، دکمه ((تأیید ✅)) را فشار دهید.\n' \
                   f'همچنین میتوانید درصورت تمایل برای تغییر ارز پایه به ارزی دیگر، ' \
                   f'نماد ارز مربوطه را همینجا ارسال کنید.'
            button_array_array = [[KeyboardButton(text='تأیید ✅'), KeyboardButton(text='لغو ❌')]]
            reply_markup = ReplyKeyboardMarkup(
                button_array_array, resize_keyboard=True, one_time_keyboard=False, selective=False)

            # Update user progress to new stage and with value
            person.person_progress = json.dumps(
                {'stage': 'AddPair_Confirm',
                 'value': {'currency': progress['value']['currency'], 'base': progress['value']['base']}})
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
            mssg = 'جفت ارز مورد نظر در صرافی کوکوین یافت نشد. لطفا ارز پایه ی دیگری را امتحان کنید.'
            try:
                context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg)
            except Exception as e:
                print(e)
                context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e))

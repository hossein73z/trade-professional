import json
import traceback

from colorama import Fore
from kucoin.client import Client
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, Message, KeyboardButton
from telegram.ext import CallbackContext

from Functions.SpecialButtonsFunction import back_button, add_exchange
from Functions.KeyboardFunctions import get_button_array_array
from Functions.DatabaseCRUD import update_person, read, exchanges_table
from Functions.FormatText import FormatText
from Objects.Person import Person
from Objects.Exchange import Exchange


def add_kucoin(person: Person, update: Update, context: CallbackContext):
    # Initialize Progress Stage
    try:
        progress = json.loads(person.person_progress)
    except Exception as e:
        progress = None
        print('Person Progress To JSON Error: ', e)

    button_array_array = get_button_array_array(person, person.person_last_button_id)
    reply_markup = ReplyKeyboardMarkup(button_array_array, True)
    if progress['value']['api_auth']['api_key'] is None:
        exchanges = read(table=exchanges_table, my_object=Exchange, api_key=update.effective_message.text, name='KuCoin')
        if exchanges is None:
            progress['value']['api_auth']['api_key'] = update.effective_message.text
            person.person_progress = json.dumps(progress)
            update_person(person)

            mssg = 'دریافت شد.\nاکنون عبارت api_secret خود را ارسال کنید'
            try:
                context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
            except Exception as e:
                print(traceback.format_exc(), e)
                context.bot.sendMessage(chat_id=person.person_chat_id, text=e, reply_markup=reply_markup)
        else:
            mssg = 'این کلید از قبل در دیتابیس وجود دارد. لطفا دوباره امتحان کنید'
            try:
                context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
            except Exception as e:
                print(traceback.format_exc(), e)
                context.bot.sendMessage(chat_id=person.person_chat_id, text=e, reply_markup=reply_markup)
        context.bot.deleteMessage(chat_id=person.person_chat_id, message_id=update.effective_message.message_id)

    elif progress['value']['api_auth']['api_secret'] is None:
        progress['value']['api_auth']['api_secret'] = update.effective_message.text
        person.person_progress = json.dumps(progress)
        update_person(person)

        mssg = 'رمز API خود را نیز ارسال کنید. دقت کنید که این رمز را در زمان ساخت API تعیین کرده اید و با رمز اکنت یا رمز ترید شما متفاوت است'
        try:
            context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
        except Exception as e:
            print(traceback.format_exc(), e)
            context.bot.sendMessage(chat_id=person.person_chat_id, text=e, reply_markup=reply_markup)
        context.bot.deleteMessage(chat_id=person.person_chat_id, message_id=update.effective_message.message_id)

    elif progress['value']['api_auth']['api_passphrase'] is None:
        progress['value']['api_auth']['api_passphrase'] = update.effective_message.text
        person.person_progress = json.dumps(progress)
        update_person(person)

        # Send user the waiting message
        mssg = 'در حال دریافت اطلاعات. لطفا منتظ بمانید'
        try:
            message = context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
        except Exception as e:
            print(traceback.format_exc(), e)
            message = context.bot.sendMessage(chat_id=person.person_chat_id, text=e, reply_markup=reply_markup)
        context.bot.deleteMessage(chat_id=person.person_chat_id, message_id=update.effective_message.message_id)

        exchanges = read(table=exchanges_table, my_object=Exchange, api_key=update.effective_message.text)
        if exchanges is None:
            exchange = Exchange(
                None,
                person.person_id,
                'KuCoin',
                progress['value']['api_auth']['api_key'],
                progress['value']['api_auth']['api_secret'],
                progress['value']['api_auth']['api_passphrase'],
                False)

            try:
                client = Client(
                    api_key=exchange.api_key,
                    api_secret=exchange.api_secret,
                    passphrase=exchange.api_passphrase,
                    sandbox=exchange.api_sandbox)
                accounts = client.get_accounts()

                balance = 0
                symbols = "USDT"
                for account in accounts:
                    symbols += "," + account['currency']

                prices = client.get_fiat_prices(base='USD', symbol=symbols)

                for account in accounts:
                    balance += float(account['balance']) * float(prices[account['currency']])

                balance = balance / float(prices['USDT'])
                balance = round(balance, 2)

                mssg = f'اکانت مورد نظر با موفقیت در سرور کوکوین یافت شد. مقدار کل دارای تقریبی این اکانت در لحظه ارسال این پیام تقریبا معادل {balance} تتر میباشد. در صورت تایید لطفا برای ثبت نهایی کلید تایید را فشار دهید.'
                reply_markup.keyboard.insert(0, [KeyboardButton(text='تأیید ✅')])

            except Exception as e:
                print(traceback.format_exc(), e)
                mssg = 'اکانتی با این مشخصات API در سرور کوکوین یافت نشد. این به این معنی است که حداقل یکی از 3 مقدار وارد شده صحیح نبوده اند. عملیات افزودن صرافی کنسل شد. در صورت تمایل میتوانید با دکمه افزودن و اطلاعات صحیح، صرافی مد نظر خود را ثبت کنید'
                person.person_progress = ''
                temp = back_button(person)
                if temp is not None:
                    reply_markup = temp['reply_keyboard_markup']

            try:
                context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
                context.bot.deleteMessage(chat_id=person.person_chat_id, message_id=message.message_id)
            except Exception as e:
                print(traceback.format_exc(), e)
                context.bot.sendMessage(chat_id=person.person_chat_id, text=e, reply_markup=reply_markup)

        else:
            mssg = 'این کلید از قبل در دیتابیس وجود دارد'
            person.person_progress = ''
            temp = back_button(person)
            if temp is not None:
                reply_markup = temp['reply_keyboard_markup']
            try:
                context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
            except Exception as e:
                print(traceback.format_exc(), e)
                context.bot.sendMessage(chat_id=person.person_chat_id, text=e, reply_markup=reply_markup)

    elif update.effective_message.text == 'تأیید ✅':
        exchanges = read(table=exchanges_table, my_object=Exchange, api_key=update.effective_message.text)
        if exchanges is None:
            person_id = person.person_id
            exchange = Exchange(
                None,
                person_id,
                'KuCoin',
                progress['value']['api_auth']['api_key'],
                progress['value']['api_auth']['api_secret'],
                progress['value']['api_auth']['api_passphrase'],
                False)

            add_exchange(exchange)

            mssg = 'صرافی کوکوین با موفقیت ثبت شد'
            person.person_progress = ''
            temp = back_button(person)
            if temp is not None:
                reply_markup = temp['reply_keyboard_markup']
            try:
                context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=ReplyKeyboardRemove())
            except Exception as e:
                print(traceback.format_exc(), e)
                context.bot.sendMessage(chat_id=person.person_chat_id, text=e, reply_markup=ReplyKeyboardRemove())

        else:
            mssg = 'این کلید از قبل در دیتابیس وجود دارد'
            person.person_progress = ''
            temp = back_button(person)
            if temp is not None:
                reply_markup = temp['reply_keyboard_markup']
            try:
                context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
            except Exception as e:
                print(traceback.format_exc(), e)
                context.bot.sendMessage(chat_id=person.person_chat_id, text=e, reply_markup=reply_markup)

        exchanges: list[Exchange] = read(table=exchanges_table, my_object=Exchange, person_id=person.person_id)
        if exchanges is not None:
            # Send user the waiting message
            mssg = 'در حال دریافت اطلاعات. لطفا منتظر بمانید'
            try:
                message: Message = context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg)
            except Exception as e:
                print(traceback.format_exc(), e)
                message: Message = context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e))

            values = []
            for exchange in exchanges:
                if exchange.name == 'KuCoin':
                    value = {'name': exchange.name, 'balance': 0}
                    try:
                        client = Client(
                            api_key=exchange.api_key,
                            api_secret=exchange.api_secret,
                            passphrase=exchange.api_passphrase,
                            sandbox=exchange.api_sandbox)
                        accounts = client.get_accounts()

                        balance = 0
                        symbols = "USDT"
                        for account in accounts:
                            symbols += "," + account['currency']

                        prices = client.get_fiat_prices(base='USD', symbol=symbols)

                        for account in accounts:
                            balance += float(account['balance']) * float(prices[account['currency']])

                        balance = balance / float(prices['USDT'])
                        value['balance'] = str(round(balance, 2)) + ' USDT'
                        values.append(value)

                    except Exception as e:
                        print(traceback.format_exc(), e)

            mssg = "حطایی پیش آمده"
            if len(values) > 0:
                mssg = FormatText.create_table_for_exchanges(['Exchange', 'Balance'], values, {'Balance': 'l'})
                mssg = f"`{mssg}`"

            try:
                context.bot.sendMessage(
                    chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup, parse_mode='Markdown')
                context.bot.deleteMessage(chat_id=person.person_chat_id, message_id=message.message_id)
            except Exception as e:
                print(traceback.format_exc(), e)
                context.bot.sendMessage(
                    chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup, parse_mode='Markdown')

    else:
        print(Fore.YELLOW + "Wrong Message" + Fore.RESET)
        mssg = "پیام نامفهوم بود.\nلطفا یکی از گزینه های زیر را انتخاب کنید"
        try:
            context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg)
        except Exception as e:
            print(traceback.format_exc(), e)
            context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e))



import json
import traceback

from kucoin.client import Client
from telegram import ReplyKeyboardMarkup, Update, KeyboardButton, Message
from telegram.ext import CallbackContext

from Functions.DatabaseCRUD import *
from Functions.Exchanges.RegisterKuCoinAPIToDatabase import add_kucoin
from Objects.Exchange import Exchange
from Objects.Person import Person
from Functions.FormatText import FormatText
from Functions.KeyboardFunctions import get_button_array_array


def exchange_button(person: Person, context: CallbackContext, reply_markup: ReplyKeyboardMarkup):
    exchanges: list[Exchange] = read(table=exchanges_table, my_object=Exchange, person_id=person.person_id)
    if exchanges is not None:
        mssg = 'در حال دریافت اطلاعات. لطفا منتظر بمانید'
        try:
            message: Message = context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg,
                                                       reply_markup=reply_markup)
        except Exception as e:
            print(traceback.format_exc(), e)
            message: Message = context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e),
                                                       reply_markup=reply_markup)

        values = []
        for exchange in exchanges:
            if exchange.name == 'KuCoin':
                value = {'name': exchange.name, 'balance': 0}
                try:
                    # Send user the waiting message
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
        mssg = 'شما هوز صرافی ثبت نکرده اید. از دکمه افزودن برای ثبت صرافی استفاده کنید'
        try:
            context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
        except Exception as e:
            print(traceback.format_exc(), e)
            context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)


def add_exchange_button(person: Person, context: CallbackContext):
    # Request user choose exchange
    mssg = 'صرافی مد نظر خود را از دکمه های زیر انتخاب کنید'
    button_array_array = get_button_array_array(person, person.person_last_button_id)
    button_array_array.insert(0, [KeyboardButton(text='کوکوین (KuCoin)')])
    reply_markup = ReplyKeyboardMarkup(button_array_array, resize_keyboard=True)
    try:
        context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
    except Exception as e:
        print(e)
        context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)

    # Change person progress to ((AddPair)) stage
    person.person_progress = json.dumps({'stage': 'AddExchange_Name', 'value': None})
    update_person(person)


def add_exchange_name(person: Person, update: Update, context: CallbackContext):
    text = update.effective_message.text
    text_lower = text.replace(" ", "")
    text_lower = text_lower.lower()
    if text == 'کوکوین (KuCoin)' or text_lower == 'کوکوین' or text_lower == 'کوکین' or text_lower == 'kucoin':
        person.person_progress = json.dumps(
            {'stage': 'AddExchange_API', 'value': {'exchange': 'KuCoin',
                                                   'api_auth': {'api_key': None,
                                                                'api_secret': None,
                                                                'api_passphrase': None,
                                                                'api_sandbox': False}}})
        update_person(person)
        mssg = 'کد api_key خود را ارسال'
        button_array_array = get_button_array_array(person, person.person_last_button_id)
        reply_markup = ReplyKeyboardMarkup(button_array_array, resize_keyboard=True)
        try:
            context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
        except Exception as e:
            print(traceback.format_exc(), e)
            context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)

    else:
        mssg = 'پیام مفهوم نبود. لطفا صرافی مد نظر را از پایین این صفحه انتخاب کنید'
        button_array_array = get_button_array_array(person, person.person_last_button_id)
        button_array_array.insert(0, [KeyboardButton(text='کوکوین (KuCoin)')])
        reply_markup = ReplyKeyboardMarkup(button_array_array, resize_keyboard=True)
        try:
            context.bot.sendMessage(chat_id=person.person_chat_id, text=mssg, reply_markup=reply_markup)
        except Exception as e:
            print(traceback.format_exc(), e)
            context.bot.sendMessage(chat_id=person.person_chat_id, text=str(e), reply_markup=reply_markup)


def add_exchange_kucoin(person: Person, update: Update, context: CallbackContext):
    add_kucoin(person, update, context)

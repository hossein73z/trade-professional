import json
import os

import psycopg2
from colorama import Fore

from Objects.Order import Order
from Objects.Exchange import Exchange
from Objects.Favorite import Favorite
from Objects.MyObject import MyObject
from Objects.Person import Person
from Objects.RawButton import RawButton
from Objects.RawSpecialButton import RawSpecialButton

persons_table = 'persons'
raw_buttons_table = 'raw_keyboard_buttons'
raw_special_buttons_table = 'raw_special_keyboard_buttons'
favorites_table = "favorites"
exchanges_table = "exchanges"
orders_table = "orders"


# Create Connection to database
def connect_database():
    my_database = psycopg2.connect(
        database=str(os.environ.get('db_name')),
        user=os.environ.get('db_user'),
        password=os.environ.get('db_password'),
        host=os.environ.get('db_host'),
        port=os.environ.get('db_port'))
    return my_database


# Initialize database
def initialize_database():
    # Create persons_table
    create_persons_table()
    # Create raw_buttons_table
    create_raw_buttons_table()
    # Create raw_special_buttons_table
    create_raw_special_buttons_table()
    # Create exchanges_table
    create_exchanges_table()
    # Create favorites_table
    create_favorites_table()
    # Create orders_table
    create_orders_table()

    # Delete items from raw_buttons_table
    for i in range(16):
        delete(table=raw_buttons_table, id=i)

    # Insert values into raw_buttons_table
    add_raw_button(RawButton(0, '/start', False, None, None, '[[1,2],[3],[4]]', None))
    add_raw_button(RawButton(1, 'بازار 💹', False, None, 0, '[[5,6],[2]]', '[[2],[0]]'))
    add_raw_button(RawButton(2, 'معاملات ⚖️', False, None, 0, '[[13]]', '[[0]]'))
    add_raw_button(RawButton(3, 'تنظیمات ⚙️', False, None, 0, '[[7],[8],[9,10]]', '[[0]]'))
    add_raw_button(RawButton(4, 'بخش مدیریت 🕴️', False, None, 0, None, '[[0]]'))
    add_raw_button(RawButton(5, 'افزودن ارز جدید ➕', False, None, 1, None, '[[1]]'))
    add_raw_button(RawButton(6, 'حذف یک جفت ارز ❌', False, None, 1, None, '[[1]]'))
    add_raw_button(RawButton(7, 'صرافی ها', False, None, 3, '[[11,12]]', '[[0]]'))
    add_raw_button(RawButton(8, 'انتخاب زبان', False, None, 3, None, '[[0]]'))
    add_raw_button(RawButton(9, 'دکمه خالی 1', False, None, 3, None, '[[0]]'))
    add_raw_button(RawButton(10, 'دکمه خالی 2', False, None, 3, None, '[[0]]'))
    add_raw_button(RawButton(11, 'افزودن صرافی', False, None, 7, None, '[[1]]'))
    add_raw_button(RawButton(12, 'حذف صرافی', False, None, 7, None, '[[1]]'))
    add_raw_button(RawButton(13, 'سفارشات', False, None, 2, '[[14,15]]', '[[0]]'))
    add_raw_button(RawButton(14, 'افزودن سفارش جدید', False, None, 13, None, '[[1]]'))
    add_raw_button(RawButton(15, 'لغو سفارش', False, None, 13, None, '[[1]]'))

    # Delete items from raw_special_buttons_table
    for i in range(3):
        delete(table=raw_special_buttons_table, id=i)

    # Insert values into raw_special_buttons_table
    add_raw_special_button(RawSpecialButton(0, 'برگشت 🔙', False))
    add_raw_special_button(RawSpecialButton(1, 'لغو ❌', False))
    add_raw_special_button(RawSpecialButton(2, 'نمایش قیمت ها 🏷', False))

    print("initialize_database:", Fore.GREEN + "Initialization Complete" + Fore.RESET)


# Delete specific table and returns nothing
def drop_table(table_name: str):
    try:
        my_database = connect_database()
        my_cursor = my_database.cursor()
        my_cursor.execute(f'drop table if exists {table_name};')

        my_database.commit()
        my_database.close()
        my_cursor.close()
        print("drop_table:", Fore.GREEN + my_cursor.rowcount() + ' ' + Fore.RESET)
    except Exception as e:
        print("drop_table:", Fore.RED + str(e) + Fore.RESET)


def create_persons_table():
    """
    Creates table and returns nothing
    """

    my_database = connect_database()
    my_cursor = my_database.cursor()

    try:
        my_cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {persons_table} (
            id SERIAL PRIMARY KEY,
            chat_id INT DEFAULT NULL,
            first_name text NOT NULL,
            last_name text DEFAULT NULL,
            username text DEFAULT NULL,
            progress text DEFAULT NULL,
            is_admin BOOL NOT NULL,
            last_button_id INT NOT NULL,
            last_special_button_id INT NOT NULL
            );""")
        print(f"Create Table {persons_table}:", Fore.GREEN + "Done" + Fore.RESET)
        my_database.commit()
    except Exception as e:
        my_database.rollback()
        print(f"Create {persons_table}:", Fore.RED + str(e) + Fore.RESET)

    my_database.commit()
    my_database.close()
    my_cursor.close()


def create_raw_buttons_table():
    """
    Creates table and returns nothing
    """

    my_database = connect_database()
    my_cursor = my_database.cursor()

    try:
        my_cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {raw_buttons_table} (id SERIAL PRIMARY KEY,
                    text text NOT NULL,
                    admin_key bool NOT NULL,
                    messages text DEFAULT NULL,
                    belong_to int DEFAULT NULL,
                    keyboards text DEFAULT NULL,
                    special_keyboards text DEFAULT NULL
                    );""")
        print(f"Create Table {raw_buttons_table}:", Fore.GREEN + "Done" + Fore.RESET)
        my_database.commit()
    except Exception as e:
        my_database.rollback()
        print(f"Create {raw_buttons_table}:", Fore.RED + str(e) + Fore.RESET)

    my_database.close()
    my_cursor.close()


def create_raw_special_buttons_table():
    """
    Creates table and returns nothing
    """

    my_database = connect_database()
    my_cursor = my_database.cursor()

    try:
        my_cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {raw_special_buttons_table} (
                    id SERIAL PRIMARY KEY,
                    text text NOT NULL,
                    admin_key bool NOT NULL
                    );""")
        print(f"Create Table {raw_special_buttons_table}:", Fore.GREEN + "Done" + Fore.RESET)
        my_database.commit()
    except Exception as e:
        my_database.rollback()
        print(f"Create {raw_special_buttons_table}:", Fore.RED + str(e) + Fore.RESET)

    my_database.close()
    my_cursor.close()


def create_exchanges_table():
    """
    Creates table and returns nothing
    """

    my_database = connect_database()
    my_cursor = my_database.cursor()

    try:
        my_cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {exchanges_table} (
                    id SERIAL PRIMARY KEY,
                    person_id int NOT NULL,
                    name text NOT NULL DEFAULT 'KuCoin',
                    api_key text NOT NULL,
                    api_secret text NOT NULL,
                    api_passphrase text NOT NULL,
                    api_sandbox bool NOT NULL
                    );""")
        print(f"Create Table {exchanges_table}:", Fore.GREEN + "Done" + Fore.RESET)
        my_database.commit()
    except Exception as e:
        my_database.rollback()
        print(f"Create {exchanges_table}:", Fore.RED + str(e) + Fore.RESET)

    try:
        my_cursor.execute(
            f"""ALTER TABLE {exchanges_table}
            ADD CONSTRAINT person_foreign_key
            FOREIGN KEY (person_id)
            REFERENCES public.{persons_table}(id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
            DEFERRABLE
            INITIALLY IMMEDIATE;""")
        my_database.commit()
        print(f"Create Table {exchanges_table}:", Fore.GREEN + "person_foreign_key Added" + Fore.RESET)
    except Exception as e:
        my_database.rollback()
        print(f"Create Table {exchanges_table}:", Fore.RED + str(e) + Fore.RESET)

    my_database.close()
    my_cursor.close()


def create_favorites_table():
    """
    Creates table and returns nothing
    """

    my_database = connect_database()
    my_cursor = my_database.cursor()

    try:
        my_cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {favorites_table} (
                    id SERIAL PRIMARY KEY,
                    person_id int NOT NULL,
                    exchange int NOT NULL,
                    currency text NOT NULL,
                    base text NOT NULL DEFAULT 'USDT'
                    );""")
        print(f"Create Table {favorites_table}:", Fore.GREEN + "Done" + Fore.RESET)
        my_database.commit()
    except Exception as e:
        my_database.rollback()
        print(f"Create {favorites_table}:", Fore.RED + str(e) + Fore.RESET)

    try:
        my_cursor.execute(
            f"""ALTER TABLE {favorites_table}
            ADD CONSTRAINT person_foreign_key
            FOREIGN KEY (person_id)
            REFERENCES public.{persons_table}(id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
            DEFERRABLE
            INITIALLY IMMEDIATE;""")
        my_database.commit()
        print(f"Create Table {favorites_table}:", Fore.GREEN + "person_foreign_key Added" + Fore.RESET)
    except Exception as e:
        my_database.rollback()
        print(f"Create Table {favorites_table}:", Fore.RED + str(e) + Fore.RESET)

    try:
        my_cursor.execute(
            f"""ALTER TABLE {favorites_table}
            ADD CONSTRAINT exchange_foreign_key
            FOREIGN KEY (exchange)
            REFERENCES public.{exchanges_table}(id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
            DEFERRABLE
            INITIALLY IMMEDIATE;""")
        my_database.commit()
        print(f"Create Table {favorites_table}:", Fore.GREEN + "exchange_foreign_key Added" + Fore.RESET)
    except Exception as e:
        my_database.rollback()
        print(f"Create Table {favorites_table}:", Fore.RED + str(e) + Fore.RESET)

    my_database.close()
    my_cursor.close()


def create_orders_table():
    """
    Creates table and returns nothing
    """

    my_database = connect_database()
    my_cursor = my_database.cursor()

    try:
        my_cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {orders_table} (
                    id SERIAL PRIMARY KEY,
                    person_id int NOT NULL,
                    exchange_order_id text NOT NULL,
                    exchange int NOT NULL,
                    currency text NOT NULL,
                    base text NOT NULL DEFAULT 'USDT',
                    price float NOt NULL,
                    amount float NOT NULL,
                    value float NOT NULL,
                    is_active bool Not NULL,
                    datetime text NOT NULL
                    );""")
        print(f"Create Table {orders_table}:", Fore.GREEN + "Done" + Fore.RESET)
        my_database.commit()
    except Exception as e:
        my_database.rollback()
        print(f"Create {orders_table}:", Fore.RED + str(e) + Fore.RESET)

    try:
        my_cursor.execute(
            f"""ALTER TABLE {orders_table}
            ADD CONSTRAINT person_foreign_key
            FOREIGN KEY (person_id)
            REFERENCES public.{persons_table}(id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
            DEFERRABLE
            INITIALLY IMMEDIATE;""")
        my_database.commit()
        print(f"Create Table {orders_table}:", Fore.GREEN + "person_foreign_key Added" + Fore.RESET)
    except Exception as e:
        my_database.rollback()
        print(f"Create Table {orders_table}:", Fore.RED + str(e) + Fore.RESET)

    try:
        my_cursor.execute(
            f"""ALTER TABLE {orders_table}
            ADD CONSTRAINT exchange_foreign_key
            FOREIGN KEY (exchange)
            REFERENCES public.{exchanges_table}(id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
            DEFERRABLE
            INITIALLY IMMEDIATE;""")
        my_database.commit()
        print(f"Create Table {orders_table}:", Fore.GREEN + "exchange_foreign_key Added" + Fore.RESET)
    except Exception as e:
        my_database.rollback()
        print(f"Create Table {orders_table}:", Fore.RED + str(e) + Fore.RESET)

    my_database.close()
    my_cursor.close()


def add_person(person: Person):
    my_database = connect_database()
    my_cursor = my_database.cursor()

    sql = f"""INSERT INTO {persons_table} (
    id,
    chat_id,
    first_name,
    last_name,
    username,
    progress,
    is_admin,
    last_button_id,
    last_special_button_id
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    val = [
        person.person_id,
        person.person_chat_id,
        person.person_first_name,
        person.person_last_name,
        person.person_username,
        person.person_progress,
        person.person_is_admin,
        person.person_last_button_id,
        person.person_last_special_button_id
    ]

    if person.person_id is None:
        sql = sql.replace('id,', "", 1)
        sql = sql.replace('%s, ', "", 1)
        val.pop(0)

    try:
        my_cursor.execute(sql, val)
        my_database.commit()
        print("add_person:", Fore.GREEN + str(my_cursor.rowcount) + " Record Inserted" + Fore.RESET)
        result = my_cursor.rowcount

    except Exception as e:
        print("add_person:", Fore.RED + str(e) + Fore.RESET)
        result = None

    my_cursor.close()
    my_database.close()

    return result


def add_raw_button(button: RawButton):
    my_database = connect_database()
    my_cursor = my_database.cursor()

    sql = f"""INSERT INTO {raw_buttons_table} (
    id,
    text,
    admin_key,
    messages,
    belong_to,
    keyboards,
    special_keyboards
    ) VALUES (%s, %s, %s, %s, %s, %s, %s)"""

    val = [
        button.button_id,
        button.button_text,
        button.button_admin_key,
        button.button_messages,
        button.button_belong_to,
        json.dumps(button.button_keyboards),
        json.dumps(button.button_special_keyboards)
    ]

    if button.button_id is None:
        sql = sql.replace('id,', "", 1)
        sql = sql.replace('%s, ', "", 1)
        val.pop(0)

    try:
        my_cursor.execute(sql, val)
        my_database.commit()
        print("add_raw_button:", Fore.GREEN + str(my_cursor.rowcount) + " Record Inserted" + Fore.RESET)
        result = my_cursor.rowcount

    except Exception as e:
        print("add_raw_button:", Fore.RED + str(e) + Fore.RESET)
        result = None

    my_cursor.close()
    my_database.close()

    return result


def add_raw_special_button(button: RawSpecialButton):
    my_database = connect_database()
    my_cursor = my_database.cursor()

    sql = f"""INSERT INTO {raw_special_buttons_table} (
    id,
    text,
    admin_key
    ) VALUES (%s, %s, %s)"""

    val = [
        button.special_button_id,
        button.special_button_text,
        button.special_button_admin_key,
    ]

    if button.special_button_id is None:
        sql = sql.replace('id,', "", 1)
        sql = sql.replace('%s, ', "", 1)
        val.pop(0)

    try:
        my_cursor.execute(sql, val)
        my_database.commit()
        print("add_raw_special_button:", Fore.GREEN + str(my_cursor.rowcount) + " Record Inserted" + Fore.RESET)
        result = my_cursor.rowcount

    except Exception as e:
        print("add_raw_special_button:", Fore.RED + str(e) + Fore.RESET)
        result = None

    my_cursor.close()
    my_database.close()

    return result


def add_exchange(exchange: Exchange):
    my_database = connect_database()
    my_cursor = my_database.cursor()

    print(exchange.id)
    print(exchange.name)
    print(exchange.api_key)
    print(exchange.api_secret)
    print(exchange.api_passphrase)
    print(exchange.api_sandbox)

    sql = f'''INSERT INTO {exchanges_table} (
    id,
    person_id,
    name,
    api_key,
    api_secret,
    api_passphrase,
    api_sandbox
    ) VALUES (%s, %s, %s, %s, %s, %s, %s )'''

    val = [
        exchange.id,
        exchange.person_id,
        exchange.name,
        exchange.api_key,
        exchange.api_secret,
        exchange.api_passphrase,
        exchange.api_sandbox
    ]

    if exchange.id is None:
        sql = sql.replace('id,', "", 1)
        sql = sql.replace('%s, ', "", 1)
        val.pop(0)

    try:
        my_cursor.execute(sql, val)
        my_database.commit()
        print("add_exchange:", Fore.GREEN + str(my_cursor.rowcount) + " Record Inserted" + Fore.RESET)
        result = my_cursor.rowcount

    except Exception as e:
        print("add_exchange:", Fore.RED + str(e) + Fore.RESET)
        result = None

    my_cursor.close()
    my_database.close()

    return result


def add_favorite(favorite: Favorite):
    my_database = connect_database()
    my_cursor = my_database.cursor()

    sql = f"""INSERT INTO {favorites_table} (
    id,
    person_id,
    exchange,
    currency,
    base
    ) VALUES (%s, %s, %s, %s, %s)"""

    val = [
        favorite.favorite_id,
        favorite.favorite_person_id,
        favorite.favorite_exchange,
        favorite.favorite_currency,
        favorite.favorite_base
    ]

    if favorite.favorite_id is None:
        sql = sql.replace('id,', "", 1)
        sql = sql.replace('%s, ', "", 1)
        val.pop(0)

    try:
        my_cursor.execute(sql, val)
        my_database.commit()
        print("add_favorite:", Fore.GREEN + str(my_cursor.rowcount) + " Record Inserted" + Fore.RESET)
        result = my_cursor.rowcount

    except Exception as e:
        print("add_favorite:", Fore.RED + str(e) + Fore.RESET)
        result = None

    my_cursor.close()
    my_database.close()

    return result


def add_order(order: Order):
    my_database = connect_database()
    my_cursor = my_database.cursor()

    sql = f"""INSERT INTO {orders_table} (
    id,
    person_id,
    exchange_order_id,
    exchange,
    currency,
    base,
    price,
    amount,
    value,
    is_active,
    datetime
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    val = [
        order.order_id,
        order.order_person_id,
        order.order_exchange_order_id,
        order.order_exchange,
        order.order_currency,
        order.order_base,
        order.order_price,
        order.order_amount,
        order.order_value,
        order.order_datetime,
        order.order_is_active
    ]

    if order.order_id is None:
        sql = sql.replace('id,', "", 1)
        sql = sql.replace('%s, ', "", 1)
        val.pop(0)

    try:
        my_cursor.execute(sql, val)
        my_database.commit()
        print("add_order:", Fore.GREEN + str(my_cursor.rowcount) + " Record Inserted" + Fore.RESET)
        result = my_cursor.rowcount

    except Exception as e:
        print("add_order:", Fore.RED + str(e) + Fore.RESET)
        result = None

    my_cursor.close()
    my_database.close()

    return result


def update_person(person: Person):
    my_database = connect_database()
    my_cursor = my_database.cursor()

    try:
        # UPDATE person
        sql = f"""UPDATE {persons_table} SET 
        chat_id = %s,
        first_name = %s,
        last_name = %s,
        username = %s,
        progress = %s,
        is_admin = %s,
        last_button_id = %s,
        last_special_button_id = %s
        WHERE id = {str(person.person_id)}
        """
        val = (
            str(person.person_chat_id),
            str(person.person_first_name),
            str(person.person_last_name),
            str(person.person_username),
            str(person.person_progress),
            str(person.person_is_admin),
            str(person.person_last_button_id),
            str(person.person_last_special_button_id)
        )

        my_cursor.execute(sql, val)
        my_database.commit()
        row_count = my_cursor.rowcount
        my_cursor.close()
        my_database.close()

        print(Fore.GREEN + str(row_count) + " Record(s) Updated" + Fore.RESET)
        return row_count

    except Exception as e:
        print("update_person:", Fore.RED + str(e) + Fore.RESET)
        my_cursor.close()
        my_database.close()
        return None


def update_exchange(exchange: Exchange):
    my_database = connect_database()
    my_cursor = my_database.cursor()

    try:
        # UPDATE exchagne
        sql = f"""UPDATE {exchanges_table} SET 
        person_id = %s,
        name = %s,
        api_key = %s,
        api_secret = %s,
        api_passphrase = %s,
        api_sandbox = %s
        WHERE id = {str(exchange.id)}
        """
        val = (
            str(exchange.id),
            str(exchange.name),
            str(exchange.api_key),
            str(exchange.api_secret),
            str(exchange.api_passphrase),
            str(exchange.api_sandbox)
        )

        my_cursor.execute(sql, val)
        my_database.commit()
        row_count = my_cursor.rowcount
        my_cursor.close()
        my_database.close()

        print(Fore.GREEN + str(row_count) + " Record(s) Updated" + Fore.RESET)
        return row_count

    except Exception as e:
        print("update_exchange:", Fore.RED + str(e) + Fore.RESET)
        my_cursor.close()
        my_database.close()
        return None


def delete(table, **kwargs):
    my_database = connect_database()
    my_cursor = my_database.cursor()

    sql = f"DELETE FROM {table}"
    conditions = ''
    if len(kwargs) > 0:
        sql += ' WHERE '
        and_string = False
        for key in kwargs:
            if and_string:
                conditions += "AND "
            and_string = True
            conditions += f"{key} = '{kwargs[key]}' "
    sql += conditions

    try:
        my_cursor.execute(sql)
        my_database.commit()
        print("delete:", Fore.GREEN + f"{str(my_cursor.rowcount)} Record(s) With {conditions} Deleted" + Fore.RESET)

        result = my_cursor.rowcount

    except Exception as e:
        print("delete:", Fore.RED + str(e) + Fore.RESET)
        result = None

    # try except block below is not tested
    try:
        my_cursor.execute("ALTER SEQUENCE " + table + "_id_seq RESTART WITH 1")
        my_database.commit()
        print(f'Table {table} Sequence Reset:', Fore.GREEN + " Successful" + Fore.RESET)

    except Exception as e:
        print(f'Table {table} Sequence Reset:', Fore.RED + str(e) + Fore.RESET)

    my_cursor.close()
    my_database.close()

    return result


def read(table: str, my_object: MyObject(), **kwargs):
    my_database = connect_database()
    my_cursor = my_database.cursor()

    sql = f"SELECT * FROM {table}"
    conditions = ''
    if len(kwargs) > 0:
        sql += ' WHERE '
        and_string = False
        for key in kwargs:
            if and_string:
                conditions += "AND "
            and_string = True
            conditions += f"{key} = '{kwargs[key]}' "
    sql += conditions

    result = None
    try:
        my_cursor.execute(sql)
        results = my_cursor.fetchall()

        items: list[MyObject] = []
        for temp in results:
            item = my_object(*temp)
            items.append(item)

        result = items
        my_cursor.close()
        my_database.close()

    except Exception as e:
        print("read:", Fore.RED + str(e) + Fore.RESET)

    my_cursor.close()
    my_database.close()
    return None if len(result) < 1 else result

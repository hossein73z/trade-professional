import os

import psycopg2
from colorama import Fore

from Objects.Exchange import Exchange
from Objects.Favorite import Favorite
from Objects.MyObject import MyObject
from Objects.Person import Person

persons_table = 'persons'
raw_buttons_table = 'raw_keyboard_buttons'
raw_special_buttons_table = 'raw_special_keyboard_buttons'
favorites_table = "favorites"
exchanges_table = "exchanges"


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
    try:
        my_database = connect_database()
        my_cursor = my_database.cursor()

        try:
            # Create persons_table
            try:
                my_cursor.execute(
                    f"""CREATE TABLE IF NOT EXISTS {persons_table} (id SERIAL PRIMARY KEY,
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

            # Create raw_buttons_table
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

            # Create raw_special_buttons_table
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

            # Create favorites_table
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

            # Create exchanges_table
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

            # Insert values into raw_buttons_table
            try:
                my_cursor.execute(
                    f"""INSERT INTO {raw_buttons_table} (id, text, admin_key, messages, belong_to, keyboards, special_keyboards)
                            VALUES
                            (0, '/start', FALSE, NULL, 0, '[[1,2],[3],[4]]', NULL),
                            (1, 'بازار 💹', FALSE, NULL, 0, '[[5,6],[2]]', '[[0]]'),
                            (2, 'معاملات ⚖️', FALSE, NULL, 0, '[[]]', '[[0]]'),
                            (3, 'تنظیمات ⚙️', FALSE, NULL, 0, '[[]]', '[[0]]'),
                            (4, 'بخش مدیریت 🕴️', FALSE, NULL, 0, '[[]]', '[[0]]'),
                            (5, 'افزودن ارز جدید ➕', FALSE, NULL, 1, NULL, '[[0]]'),
                            (6, 'حذف یک جفت ارز ❌', FALSE, NULL, 1, NULL, '[[0]]');""")
                print(f"Insert Values to {raw_buttons_table}:",
                      Fore.GREEN + str(my_cursor.rowcount) + " Record Added" + Fore.RESET)
                my_database.commit()
            except Exception as e:
                my_database.rollback()
                print(f"Insert Values into {raw_buttons_table}:", Fore.RED + str(e) + Fore.RESET)

            # Insert values into raw_special_buttons_table
            try:
                my_cursor.execute(
                    f"""INSERT INTO {raw_special_buttons_table} (id, text, admin_key) VALUES
                            (0, 'برگشت 🔙', FALSE);""")
                print(f"Insert Values to {raw_special_buttons_table}:",
                      Fore.GREEN + str(my_cursor.rowcount) + " Record Added" + Fore.RESET)
                my_database.commit()
            except Exception as e:
                my_database.rollback()
                print(f"Insert Values to {raw_special_buttons_table}:", Fore.RED + str(e) + Fore.RESET)

            print("initialize_database:", Fore.GREEN + "Initialization Complete" + Fore.RESET)

        except Exception as e:
            my_database.rollback()
            print("initialize_database:", Fore.RED + str(e) + Fore.RESET)

    except Exception as e:
        print("Database Error:", Fore.RED + str(e) + Fore.RESET)


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

    my_cursor.execute(f"""CREATE TABLE IF NOT EXISTS {persons_table} (
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

    my_database.commit()
    my_database.close()
    my_cursor.close()


def create_raw_buttons_table():
    """
    Creates table and returns nothing
    """

    my_database = connect_database()
    my_cursor = my_database.cursor()

    my_cursor.execute(f"""CREATE TABLE IF NOT EXISTS {raw_buttons_table} (
    id SERIAL PRIMARY KEY,
    text text NOT NULL,
    admin_key bool NOT NULL,
    messages text DEFAULT NULL,
    belong_to int DEFAULT NULL,
    keyboards text DEFAULT NULL,
    special_keyboards text DEFAULT NULL
    );""")

    my_database.commit()
    my_database.close()
    my_cursor.close()


def create_raw_special_buttons_table():
    """
    Creates table and returns nothing
    """

    my_database = connect_database()
    my_cursor = my_database.cursor()

    my_cursor.execute(f"""CREATE TABLE IF NOT EXISTS {raw_special_buttons_table} (
    id SERIAL PRIMARY KEY,
    text text NOT NULL,
    admin_key bool NOT NULL
    );""")

    my_database.commit()
    my_database.close()
    my_cursor.close()


def create_favorites_table():
    """
    Creates table and returns nothing
    """

    my_database = connect_database()
    my_cursor = my_database.cursor()

    my_cursor.execute(f"""CREATE TABLE IF NOT EXISTS {favorites_table} (
    id SERIAL PRIMARY KEY,
    person_id int NOT NULL,
    exchange int NOT NULL,
    currency text NOT NULL,
    base text NOT NULL DEFAULT 'USDT'
    );""")

    my_database.commit()
    my_database.close()
    my_cursor.close()


def create_exchanges_table():
    """
    Creates table and returns nothing
    """

    my_database = connect_database()
    my_cursor = my_database.cursor()

    my_cursor.execute(f"""CREATE TABLE IF NOT EXISTS {exchanges_table} (
                            id SERIAL PRIMARY KEY,
                            person_id int NOT NULL,
                            name text NOT NULL DEFAULT 'KuCoin',
                            api_key text NOT NULL,
                            api_secret text NOT NULL,
                            api_passphrase text NOT NULL,
                            api_sandbox bool NOT NULL
                            );""")

    my_database.commit()
    my_database.close()
    my_cursor.close()


def add_person(person: Person):
    my_database = connect_database()
    my_cursor = my_database.cursor()

    sql = f"""INSERT INTO {persons_table} (
    chat_id,
    first_name,
    last_name,
    username,
    progress,
    is_admin,
    last_button_id,
    last_special_button_id
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""

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

    try:
        my_cursor.execute(sql, val)
        my_database.commit()
        print("add_person:", Fore.GREEN + str(my_cursor.rowcount) + "Record Inserted" + Fore.RESET)
        result = my_cursor.rowcount

    except Exception as e:
        print("add_person:", Fore.RED + str(e) + Fore.RESET)
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


def add_favorite(favorite: Favorite):
    my_database = connect_database()
    my_cursor = my_database.cursor()

    sql = f"""INSERT INTO {favorites_table} (
    person_id,
    exchange,
    currency,
    base
    ) VALUES (%s, %s, %s, %s)"""

    val = (
        str(favorite.favorite_person_id),
        str(favorite.favorite_exchange),
        str(favorite.favorite_currency),
        str(favorite.favorite_base)
    )

    try:
        my_cursor.execute(sql, val)
        my_database.commit()
        print("add_favorite:", Fore.GREEN + str(my_cursor.rowcount) + "Record Inserted" + Fore.RESET)
        result = my_cursor.rowcount

    except Exception as e:
        print("add_favorite:", Fore.RED + str(e) + Fore.RESET)
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
    person_id,
    name,
    api_key,
    api_secret,
    api_passphrase,
    api_sandbox
    ) VALUES (%s, %s, %s, %s, %s, %s )'''

    val = (
        str(exchange.person_id),
        str(exchange.name),
        str(exchange.api_key),
        str(exchange.api_secret),
        str(exchange.api_passphrase),
        str(exchange.api_sandbox)
    )

    try:
        my_cursor.execute(sql, val)
        my_database.commit()
        print("add_exchange:", Fore.GREEN + str(my_cursor.rowcount) + "Record Inserted" + Fore.RESET)
        result = my_cursor.rowcount

    except Exception as e:
        print("add_exchange:", Fore.RED + str(e) + Fore.RESET)
        result = None

    my_cursor.close()
    my_database.close()

    return result


def delete(table, **kwargs):
    my_database = connect_database()
    my_cursor = my_database.cursor()

    try:
        sql = f"DELETE FROM {table} WHERE "
        and_string = False
        for key in kwargs:
            if and_string:
                sql += "AND "
            sql += f"{key} = {kwargs[key]} "

        my_cursor.execute(sql)
        my_database.commit()
        print(Fore.GREEN + str(my_cursor.rowcount) + "Record(s) Deleted" + Fore.RESET)

        result = my_cursor.rowcount

    except Exception as e:
        print("delete_person:", Fore.RED + str(e) + Fore.RESET)
        result = None

    my_cursor.close()
    my_database.close()

    return result


def read(table: str, my_object: MyObject(), **kwargs):
    my_database = connect_database()
    my_cursor = my_database.cursor()
    try:
        sql = f"SELECT * FROM {table}"
        if len(kwargs) > 0:
            sql += ' WHERE '
            and_string = False
            for key in kwargs:
                if and_string:
                    sql += "AND "
                and_string = True
                sql += f"{key} = '{kwargs[key]}' "
        my_cursor.execute(sql)
        results = my_cursor.fetchall()

        items: list[MyObject] = []
        for temp in results:
            item = my_object(*temp)
            items.append(item)

        result = items
        my_cursor.close()
        my_database.close()
        return None if len(result) < 1 else result

    except Exception as e:
        print("read:", Fore.RED + str(e) + Fore.RESET)
        my_cursor.close()
        my_database.close()
        return None

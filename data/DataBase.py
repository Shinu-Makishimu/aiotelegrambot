import datetime
import sqlite3

from loguru import logger


from settings import NAME_DATABASE

language_dict = {
    'ru': 'ru_RU',
    'en': 'en_US'
}


def create_bd_if_not_exist() -> None:
    """
    функция создает базу данных если вдруг её нет. проверка на наличие бд в main
    :return:
    """
    logger.info(f'Function {create_bd_if_not_exist.__name__} called')
    with sqlite3.connect(NAME_DATABASE) as db:
        cursor = db.cursor()

        query = """PRAGMA foreign_keys=on;"""
        query_1 = """CREATE TABLE IF NOT EXISTS clients(
        user_id INTEGER PRIMARY KEY NOT NULL,
        language TEXT,
        status TEXT,
        FOREIGN KEY (user_id) REFERENCES requests (user_id)
        );"""
        query_2 = """CREATE TABLE IF NOT EXISTS requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        command TEXT,
        city TEXT,
        city_name, TEXT
        request_date TEXT,
        hotel_count TEXT,
        photo_count TEXT,
        distance TEXT,
        min_price TEXT,
        max_price TEXT,
        currency TEXT);"""

        cursor.execute(query)
        cursor.execute(query_2)
        cursor.execute(query_1)
        db.commit()


def create_user_in_db(user_id: str) -> None:
    """
    Функция создаёт пользователя в базе данных

    :param user_id: id пользователя
    :param language: язык пользователя
    :return: None
    """
    logger.info(f'Function {create_user_in_db.__name__} called and use args: user_id{user_id}')

    status = 'user'
    language = 'en_US'

    with sqlite3.connect(NAME_DATABASE) as db:
        cursor = db.cursor()
        request = """INSERT INTO clients VALUES (?,?,?);"""
        cursor.execute(
            request,
            (
                user_id,
                language,
                status
            )
        )
        db.commit()


def check_user_in_db(user_id: str) -> bool:
    """
    Функция проверяет наличие присутствия пользователя в базе данных

    :param user_id: id пользователя
    :return: True если пользователь найден, иначе False
    """
    logger.info(f'Function {check_user_in_db.__name__} called and use args: user_id\t{user_id}')

    with sqlite3.connect(NAME_DATABASE, check_same_thread=False) as db:
        cursor = db.cursor()
        cursor.execute("""SELECT user_id FROM clients WHERE user_id=:user_id""", {'user_id': user_id})
        response = cursor.fetchone()

    if response is None:
        logger.info(f"user wasn't found in sqlite")
        return False
    else:
        logger.info(f"user was found in sqlite")
        return True


def get_user_from_bd(user_id: str) -> list[str]:
    """
    функция добывания пользователя из базы данных
    :param user_id: id пользователя
    :return: список данных о пользователе
    """
    logger.info(f'Function {get_user_from_bd.__name__} called use args: user_id\t{user_id}')

    with sqlite3.connect(NAME_DATABASE) as db:
        cursor = db.cursor()
        cursor.execute("""SELECT * FROM clients WHERE user_id=:user_id""",
                       {'user_id': user_id})
        response = cursor.fetchall()

        logger.info(f'I get this information in sqlite: {response[0]}')

        return response[0]


def create_history_record(user_id: str, query: dict) -> None:
    """
    Функция записи в базу данных параметров запроса отелей для формирования историии
    :param user_id: id пользователя
    :param hist_dict: словарь, содержащий подготовленные к записи в бд параметры
    :return: None
        parameters = {
        'city': user_data['city_id'],
        'hotel_count': user_data['hotel_number'],
        'photo_count': user_data['photo_number'],
        'command': 'lowprice',
        'currency': user_data['currency'],
        'language': language
    }
    user_id INTEGER NOT NULL,
        command TEXT,
        city TEXT,
        city_name, TEXT
        request_date TEXT,
        hotel_count TEXT,
        photo_count TEXT,
        distance TEXT,
        min_price TEXT,
        max_price TEXT,
        currency TEXT);
    """
    logger.info(f'Function {create_history_record.__name__} called with arguments: '
                f'user_id {user_id}\thist_dict\n{query}')

    with sqlite3.connect(NAME_DATABASE) as db:
        cursor = db.cursor()
        request = """INSERT INTO requests VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?) """
        cursor.execute(
            request,
            (
                user_id,  # 2
                query['command'],  # 3
                query['city'],  # 4
                query['city_name'], # 5
                query['req_date'],  # 6
                query['hotel_count'],  # 7
                query['photo_count'],  # 8
                query['distance'],  # 9
                query['min_price'],  # 10
                query['max_price'],  # 11
                query['currency']  # 12
            )
        )
        db.commit()


def get_history_from_db(user_id: str, short=False) -> list[str]:
    """
    функция получения истории поиска.
    :param short: Параметр (по умолчанию False) настраивающий выдачу из бд.
        True - короткая выдача: id записи, команда на поиск, название города.
        False - полная выдача. id записи, id города, команда на поиск, дата запроса, количество отелей в выдаче,
            количество фото, минимальная, максимальная цена, радиус поиска.
    :param user_id: id пользователя
    :return: список поисковывых запросов в виде кортежей строк
    """
    logger.info(f'Function {get_history_from_db.__name__} called with argument: user_ id {user_id}')
    if short:
        with sqlite3.connect(NAME_DATABASE) as db:
            cursor = db.cursor()
            cursor.execute("""SELECT id, command, city_name FROM requests WHERE user_id=:user_id""",
                           {'user_id': user_id})
            response = cursor.fetchall()
            logger.info(f'Get response from db \n{response}')
    else:
        with sqlite3.connect(NAME_DATABASE) as db:
            cursor = db.cursor()
            cursor.execute("""SELECT * FROM requests WHERE user_id=:user_id""",
                           {'user_id': user_id})
            response = cursor.fetchall()
            logger.info(f'Get response from db \n{response}')
    return response


def set_history(user_id: str, parameters: dict) -> None:
    """
    Функция подготавливает поисковые параметры к записи в базу данных sqlite
    :param parameters:
    :param user_id: id пользователя
    :return: None

        parameters = {
        'city': user_data['city_id'],
        'hotel_count': user_data['hotel_number'],
        'photo_count': user_data['photo_number'],
        'command': 'lowprice',
        'currency': user_data['currency'],
        'language': language
    }
    """
    logger.info(f'Function {set_history.__name__} called with argument: '
                f'user_id {parameters}')
    if not check_user_in_db(user_id):
        create_user_in_db(user_id, )
    command = parameters['command']

    if command in ['lowprice', 'highprice']:
        parameters.update({'min_price': '-'})
        parameters.update({'max_price': '-'})
        parameters.update({'distance': '-'})
    create_history_record(user_id=user_id, query=parameters)



def prepare_history_for_search(user_id: int or str) -> None:
    """
    Функция подготавливает запрос из истории запросов к повторному использованию
    :param user_id: id пользователя
    :return: None
    """
    logger.info(f'function {prepare_history_for_search.__name__} was called')
    history_record = get_history_from_db(user_id=user_id)
    record_id = get_settings(user_id=user_id, key='history_id')
    record = ()

    for i_rec in range(len(history_record)):
        if int(history_record[i_rec][0]) == int(record_id):
            record = history_record[i_rec]

    set_settings(user_id, 'city', record[3])
    set_settings(user_id, 'hotel_count', record[6])
    set_settings(user_id, 'photo_count', record[7])
    set_settings(user_id, 'date1', record[11])
    set_settings(user_id, 'date2', record[12])
    set_settings(user_id, 'command', record[2])
    set_settings(user_id, 'currency', record[13])
    set_settings(user_id, 'city_name', record[4])

    if record[2] == 'bestdeal':
        set_settings(user_id, 'max_price', record[10])
        set_settings(user_id, 'min_price', record[9])
        set_settings(user_id, 'distance',  record[8])

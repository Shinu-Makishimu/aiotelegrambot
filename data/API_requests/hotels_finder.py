import re
import requests
from typing import Any, Union, Dict
from loguru import logger

# from accessory import get_date
# from database import get_settings
# from language import interface
from settings import H_API_TOKEN
from data.API_requests.photos import make_photo_list

order = {
    'lowprice': 'PRICE',
    'highprice': 'PRICE_HIGHEST_FIRST',
    'bestdeal': 'DISTANCE_FROM_LANDMARK'
}


def get_hotels(params: Dict ) -> Dict or None:
    """
    Функция получает юзер айди, на его основе формирует с помощью вспомогательных функций список результатов
    :param user_id:
    :return: если сайт вернул bad request, возвращает bad request, если результата нет, none
     иначе словарь с результатами
    """

    logger.info(f'function {get_hotels.__name__} was called with  {params}')

    data = request_hotels(p=params)

    if 'bad_request' in data:
        return {'bad_request': 'bad_request'}

    data = structure_hotels_info(user_id=user_id, data=data)

    if not data or len(data['results']) < 1:
        return None
    if params['command'] == 'bestdeal':
        next_page = data.get('next_page')
        distance = float(params['distance'])
        while next_page and next_page < 5 \
                and float(data['results'][-1]['distance'].replace(',', '.').split()[0]) <= distance:
            add_data = request_hotels(p=params, page=next_page)
            if 'bad_req' in data:
                logger.warning('bad_request')
                break
            add_data = structure_hotels_info(user_id=user_id, data=add_data)
            if add_data and len(add_data["results"]) > 0:
                data['results'].extend(add_data['results'])
                next_page = add_data['next_page']
            else:
                break
        max_hotels_numbers = int(params['hotel_count'])
        data = choose_best_hotels(hotels=data['results'], distance=distance, limit=max_hotels_numbers)
    else:
        data = data['results']

    data = generate_hotels_descriptions(hotels=data, user_id=user_id)
    return data


def request_hotels(p: Dict, page=1) -> Dict:
    """
    функция запроса списка отелей из апи

    :param p:
    :param page:
    :return: возвращает словарь
    """
    logger.info(f'Function {request_hotels.__name__} called with argument: parameters = {p}')
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {
        "destinationId": p['city'],
        "pageNumber": str(page),
        "pageSize": p['hotel_count'],
        "checkIn": get_date(int(p['date1'])),
        "checkOut": get_date(int(p['date2'])),
        "adults1": "1",
        "sortOrder": order[p['command']],
        "locale": p['language'],
        "currency": p['currency']
    }

    if p['command'] == 'bestdeal':
        querystring['priceMax'] = p['max_price']
        querystring['priceMin'] = p['min_price']
        querystring['pageSize'] = '25'
    logger.info(f'Search parameters: {querystring},')

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': H_API_TOKEN
    }
    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=20)
        data = response.json()
        if data.get('message'):
            raise requests.exceptions.RequestException
        logger.info(f'Hotels api(properties/list) response received: {data}')
        return data

    except Exception as error:
        logger.error(f'Error receiving response: {error}')
        return {'bad_request': 'bad_request'}


def structure_hotels_info(user_id, data) -> Dict or None:
    """
    Структурирование результатов поиск для удобной обработки в дальнейшем
    :param user_id:
    :param data:
    :return:
    """
    logger.info(f'Function {structure_hotels_info.__name__} called with args user_id = {user_id}, data = {data}')
    data = data.get('data', {}).get('body', {}).get('searchResults')

    hotels = dict()
    try:
        hotels['total_count'] = data.get('totalCount', 0)
    except AttributeError as err:
        logger.error(f'Function {structure_hotels_info.__name__} was crushed with {err}')
        return None

    logger.info(f"Next page: {data.get('pagination', {}).get('nextPageNumber', 0)}")

    hotels['next_page'] = data.get('pagination', {}).get('nextPageNumber')
    hotels['results'] = []
    lang = get_settings(user_id=user_id, key='language')
    if hotels['total_count'] > 0:
        for i_hotel in data.get('results'):
            hotel = dict()
            hotel['name'] = i_hotel.get('name')
            hotel['id'] = i_hotel.get('id')
            hotel['star_rating'] = i_hotel.get('starRating', 0)
            hotel['price'] = hotel_price(i_hotel, lang, user_id)
            if not hotel['price']:
                continue
            hotel['distance'] = i_hotel.get(
                'landmarks')[0].get(
                    'distance',
                    interface['errors']['no_information'][lang]
            )
            hotel['address'] = hotel_address(i_hotel, lang=lang)
            hotel['coordinates'] = i_hotel.get('coordinate')
            if hotel not in hotels['results']:
                hotels['results'].append(hotel)
        logger.info(f'Hotels in function {structure_hotels_info.__name__}: {hotels}')
        return hotels


def choose_best_hotels(hotels: list[dict], distance: float, limit: int) -> list[dict]:
    """
    фильтрация  отелей по дистанции.
    :param hotels: Список словарей отелей
    :param distance: дистанция в километрах
    :param limit: ограничение на количество отелей в списке
    :return:
    """
    logger.info(f'Function {choose_best_hotels.__name__} called with arguments: '
                f'distance = {distance}, quantity = {limit}\n{hotels}')
    hotels = list(filter(lambda x: float(x["distance"].strip().replace(',', '.').split()[0]) <= distance, hotels))
    hotels = sorted(hotels, key=lambda x: x["price"])
    if len(hotels) > limit:
        hotels = hotels[:limit]
    return hotels


def generate_hotels_descriptions(hotels: Dict, user_id: str) -> Dict[Any, Dict[str, Union[str, list[str]]]]:
    """
    формирование словаря с сообщением для вывода пользователю и фотографиями

    :param hotels: словарь с отелями
    :param user_id: id пользователя
    :return: hotels_info =
                {
                    "hotel_ID":
                        {
                            "photo": список изображений
                            "message": сформированный ответ для пользователя
                        }
                }
    """
    logger.info(f'Function {generate_hotels_descriptions.__name__} called with argument {hotels}')
    hotels_info = dict()
    lang = get_settings(user_id=user_id, key='language')
    photo_number = get_settings(user_id=user_id, key='photo_count')
    currency = get_settings(user_id=user_id, key='currency')
    for hotel in hotels:
        photo = make_photo_list(
            hotel_id=hotel.get('id'),
            counter=int(photo_number)
        )
        hot_rat = hotel_rating(rating=hotel.get('star_rating'), lang=lang)

        lang_hotel = interface['elements']['hotel'][lang],
        name_hotel = hotel.get('name'),
        rating_hotel = interface['elements']['rating'][lang],
        rat_h = hot_rat,
        pri_hot = interface['elements']['price'][lang],
        price = str(hotel['price']) + ' ' + currency,
        dis_h = interface['elements']['distance'][lang],
        dist = hotel.get('distance'),
        addr_h = interface['elements']['address'][lang],
        addr = hotel.get('address'),
        link = google_maps_link(coordinates=hotel['coordinates'], lang=lang)

        # message = (
        #     f"{interface['elements']['hotel'][lang]}: "
        #     f"{hotel.get('name')}\n"
        #
        #     f"{interface['elements']['rating'][lang]}: "
        #     f"{hotel_rating(rating=hotel.get('star_rating'), lang=lang)}\n"
        #
        #     f"{interface['elements']['price'][lang]}: "
        #     f"{hotel['price']} {get_settings(user_id=user_id, key='currency')}\n"
        #
        #     f"{interface['elements']['distance'][lang]}: "
        #     f"{hotel.get('distance')}\n"
        #
        #     f"{interface['elements']['address'][lang]}: "
        #     f"{hotel.get('address')}\n"
        #
        #     f"{interface['elements']['g_link'][lang]}: "
        #     f"{google_maps_link(coordinates=hotel['coordinates'],lang=lang)}\n"
        #
        # )

        message = (
            f"{lang_hotel[0]}: "
            f"{name_hotel[0]}\n"
            f"{rating_hotel[0]}: "
            f"{rat_h[0]}\n"
            f"{pri_hot[0]}: "
            f"{price[0]}\n"
            f"{dis_h[0]}: "
            f"{dist[0]}\n"
            f"{addr_h[0]}: "
            f"{addr[0]}\n"
            f"{link}\n")

        hotels_info.update(
            {
                hotel.get('name'):
                    {
                        "message": message,
                        "photo": photo
                    }
            })
    return hotels_info


def hotel_price(hotel, lang, user_id) -> float or str:
    """
    Функция формирует цену отеля. количество дней проживания перемножается на стоимость суток.

    :param hotel: словарь с данными отеля полученными от api
    :param lang: язык пользователя
    :param user_id:  id пользователя
    :return: возвращаем цену, округленную до двух знаков. Если цену получить не удалось, возвращаем "нет данных"
    """
    logger.info(f'Function {hotel_price.__name__} called with argument {hotel}')
    check_in = int(get_settings(user_id=user_id, key='date1'))
    check_out = int(get_settings(user_id=user_id, key='date2'))
    days_number = days_count(check_in=check_in, check_out=check_out)
    try:
        if hotel.get('ratePlan').get('price').get('exactCurrent'):
            temp_price = hotel.get('ratePlan').get('price').get('exactCurrent')
        else:
            temp_price = hotel.get('ratePlan').get('price').get('current')
            temp_price = int(re.sub(r'[^0-9]', '', temp_price))
        price = round(days_number * temp_price, 2)
    except Exception as error:
        logger.warning(f'price crushed with {error}')
        price = interface['errors']['no_information'][lang]
    return price


def hotel_address(hotel: dict, lang: str) -> str:
    """
    Функция формирования адреса. Если адреса нет, возвращаем нет данных
    :param hotel: словарь с данными отеля полученными из API
    :param lang:  язык пользователя
    :return: строка с адресом, если адреса нет, возвращаем нет данных
    """
    logger.info(f'Function {hotel_address.__name__} called with argument {hotel}')
    message = interface['errors']['no_information'][lang]
    if hotel.get('address'):
        message = hotel.get('address').get('streetAddress', message)
    return message


def hotel_rating(rating: float, lang: str) -> str:
    """
    Рейтинг отеля.
    :param rating: число звезд.
    :param lang: язык
    :return: возвращает строку с количеством звездочек, равными рейтингу отеля, если
    информации нет то возвращает строку нет данных
    """
    logger.info(f'Function {hotel_rating.__name__} called with {rating}')
    if not rating:
        return interface['errors']['no_information'][lang]
    return '⭐' * int(rating)


def google_maps_link(coordinates: dict, lang: str) -> str:
    """
    формирует ссылку на карты гугл.
    :param coordinates: словарь с широтой и долготой
    :param lang: язык пользователя
    :return: строка ссылки или нет данных
    """
    if not coordinates:
        return interface['errors']['no_information'][lang]
    text = interface['elements']['g_link'][lang]
    link = f"http://www.google.com/maps/place/{coordinates['lat']},{coordinates['lon']}"
    r = f'<a href="{link}">{text}</a>'
    return r


def days_count(check_in: int, check_out: int):
    """
    счетчик дней для вычисления итоговой стоимости проживания
    :param check_in: дата заезда
    :param check_out: дата выезда
    :return: целое число дней
    """
    logger.info(f'Function {days_count.__name__} was called with { check_in} {check_out}')
    date_in = get_date(tmstmp=check_in, days=True)
    date_out = get_date(tmstmp=check_out, days=True)
    date_result = abs((date_out-date_in).days)
    logger.info(f'Function {days_count.__name__} make some math: { date_out} minus {date_in} = {date_result}')
    return date_result

import re
import requests
import datetime
from typing import Any, Union, Dict
from loguru import logger

from settings import H_API_TOKEN
from data.API_requests.photos import make_photo_list

order = {
    'lowprice': 'PRICE',
    'highprice': 'PRICE_HIGHEST_FIRST',
    'bestdeal': 'DISTANCE_FROM_LANDMARK'
}


def get_hotels(params: Dict ) -> Dict or None:
    """
    The function receives a dictionary of parameters. Generates a dictionary of search results using helper functions

    :return: if the site returned an invalid request, it returns an invalid request, if there is no result - None,
    otherwise a dictionary with results
    """

    logger.info(f'function {get_hotels.__name__} was called with  {params}')

    data = request_hotels(p=params)

    if 'bad_request' in data:
        return {'bad_request': 'bad_request'}

    data = structure_hotels_info(lang=params['language'], data=data)

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
            add_data = structure_hotels_info(lang=params['language'], data=add_data)
            if add_data and len(add_data["results"]) > 0:
                data['results'].extend(add_data['results'])
                next_page = add_data['next_page']
            else:
                break
        max_hotels_numbers = int(params['hotel_count'])
        data = choose_best_hotels(hotels=data['results'], distance=distance, limit=max_hotels_numbers)
    else:
        data = data['results']

    data = generate_hotels_descriptions(hotels=data, parameters=params)
    return data


def request_hotels(p: Dict, page=1) -> Dict:
    """
    This function requests a list of hotels from the API


    :param p:
    :param page:
    :return: dictionary
    """
    logger.info(f'Function {request_hotels.__name__} called with argument: parameters = {p}')
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {
        "destinationId": p['city'],
        "pageNumber": str(page),
        "pageSize": p['hotel_count'],
        "checkIn": datetime.date.today(),
        "checkOut": datetime.date.today() + datetime.timedelta(days=1),
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


def structure_hotels_info(lang, data) -> Dict or None:
    """
    Structuring search results for easy processing.

    :param data:
    :return:
    """
    logger.info(f'Function {structure_hotels_info.__name__} called with args lang = {lang}, data = {data}')
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

    if hotels['total_count'] > 0:
        for i_hotel in data.get('results'):
            hotel = dict()
            hotel['name'] = i_hotel.get('name')
            hotel['id'] = i_hotel.get('id')
            hotel['star_rating'] = i_hotel.get('starRating', 0)
            hotel['price'] = hotel_price(i_hotel)
            hotel['distance'] = i_hotel.get(
                'landmarks')[0].get(
                    'distance',
                    'Нет информации'
            )
            hotel['address'] = hotel_address(i_hotel)
            hotel['coordinates'] = i_hotel.get('coordinate')
            if hotel not in hotels['results']:
                hotels['results'].append(hotel)
        logger.info(f'Hotels in function {structure_hotels_info.__name__}: {hotels}')
        return hotels


def choose_best_hotels(hotels: list[dict], distance: float, limit: int) -> list[dict]:
    """
    Hotel filtering by distance .
    :param hotels: List of hotel dictionaries
    :param distance: distance in kilometers
    :param limit: limit on the number of hotels in the list
    :return:
    """
    logger.info(f'Function {choose_best_hotels.__name__} called with arguments: '
                f'distance = {distance}, quantity = {limit}\n{hotels}')
    hotels = list(filter(lambda x: float(x["distance"].strip().replace(',', '.').split()[0]) <= distance, hotels))
    hotels = sorted(hotels, key=lambda x: x["price"])
    if len(hotels) > limit:
        hotels = hotels[:limit]
    return hotels


def generate_hotels_descriptions(hotels: Dict, parameters: Dict) -> Dict[Any, Dict[str, Union[str, list[str]]]]:
    """
    Creating a dictionary with a message and photos to display to the user

    :param parameters:
    :param hotels: List of hotel dictionaries
    :return: hotels_info =
                {
                    "hotel_ID":
                        {
                            "photo": Photo list
                            "message": Message for send
                        }
                }
    """
    logger.info(f'Function {generate_hotels_descriptions.__name__} called with argument {hotels}')
    hotels_info = dict()
    lang = parameters['language']
    photo_number = parameters['photo_count']
    currency = parameters['currency']
    for hotel in hotels:
        photo = make_photo_list(
            hotel_id=hotel.get('id'),
            counter=int(photo_number)
        )
        hot_rat = hotel_rating(rating=hotel.get('star_rating'))

        lang_hotel = 'Hotel name ',
        name_hotel = hotel.get('name'),
        rating_hotel = 'Rating  ',
        rat_h = hot_rat,
        pri_hot = 'Price for night ',
        price = str(hotel['price']) + ' ' + currency,
        dis_h = 'Distance from centre  ',
        dist = hotel.get('distance'),
        addr_h = 'Address ',
        addr = hotel.get('address'),
        link = google_maps_link(coordinates=hotel['coordinates'])

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


def hotel_price(hotel) -> float or str:
    """
    Function create price

    :param hotel: Dictionary with information about hotel
    :return:
    """
    logger.info(f'Function {hotel_price.__name__} called with argument {hotel}')

    price = 'No information'
    if hotel.get('ratePlan').get('price').get('exactCurrent'):
        price = hotel.get('ratePlan').get('price').get('exactCurrent')
    else:
        price = hotel.get('ratePlan').get('price').get('current')

    return price


def hotel_address(hotel: dict) -> str:
    """
    Create hotel address
    :param hotel:

    :return:
    """
    logger.info(f'Function {hotel_address.__name__} called with argument {hotel}')
    message = 'No information'
    if hotel.get('address'):
        message = hotel.get('address').get('streetAddress', message)
    return message


def hotel_rating(rating: float) -> str:
    """
    Hotels rating.
    :param rating: stars number.
    :return:
    """
    logger.info(f'Function {hotel_rating.__name__} called with {rating}')
    if not rating:
        return 'No information'
    return '⭐' * int(rating)


def google_maps_link(coordinates: dict) -> str:
    """
    формирует ссылку на карты гугл.
    :param coordinates: словарь с широтой и долготой
    :return: строка ссылки или нет данных
    """
    if not coordinates:
        return 'No information'
    text = 'Google maps'
    link = f"http://www.google.com/maps/place/{coordinates['lat']},{coordinates['lon']}"
    r = f'<a href="{link}">{text}</a>'
    return r



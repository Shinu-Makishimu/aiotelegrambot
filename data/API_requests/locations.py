import re
import requests
from aiogram import types
from typing import Dict, Any

from loguru import logger
from settings import H_API_TOKEN


def make_locations_list(message: types.Message) -> Dict:
    """
    A function that generates a dictionary of locations to generate a keyboard of locations
    :param message: message object
    :return: Locations dictionary from api
    """
    logger.info(f'function {make_locations_list.__name__} was called with arg {message.text}')
    data = request_locations(message)
    if not data:
        return {'bad_request': 'bad_request'}
    locations = dict()
    if len(data.get('suggestions')[0].get('entities')) > 0:
        for item in data.get('suggestions')[0].get('entities'):
            location_name = re.sub('<([^<>]*)>', '', item['caption'])
            locations[location_name] = item['destinationId']
        return locations


def request_locations(message: types.Message) -> Dict:
    """
    Request to API
    :param message:
    :return:
    """

    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    logger.info(f'function {request_locations.__name__} was called with message and use args: '
                f'\t text: {message.text}')

    querystring = {
        "query": message.text.strip(),
        "locale": 'en_US'
    }

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': H_API_TOKEN
    }

    response = requests.request("GET", url, headers=headers, params=querystring, timeout=20)
    data = response.json()
    return data


def delete_tags(html_text: Any) -> str:
    """
    Delite html tegs in text
    :param html_text:
    :return:
    """
    logger.info(f'function {delete_tags.__name__} was called')
    text = re.sub('<([^<>]*)>', '', html_text)
    return text

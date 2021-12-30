from decouple import config

content_type_ANY = ['audio', 'document', 'photo', 'sticker', 'video', 'voice', 'contact', 'caption']

commands_list = ['/start', '/lowprice', '/highprice', '/bestdeal', '/settings', '/help']

API_TOKEN = config('KEY')  # токен бота

H_API_TOKEN = config('APIKEY')  # токен hotels

HOST = 'hotels4.p.rapidapi.com'

url = "https://hotels4.p.rapidapi.com/locations/v2/search"

NAME_DATABASE = 'bot.db'

redis_db = redis.StrictRedis(host='localhost', port=6379, db=1, charset='utf-8', decode_responses=True) # конф redis

excluded_types = ['audio', 'document', 'photo', 'sticker', 'video', 'voice']  # список непринимаемых типов данных.

search_type = {
    'lowprice': 'PRICE',
    'highprice': 'PRICE_HIGHEST_FIRST',
    'bestdeal': 'DISTANCE_FROM_LANDMARK'
}

logger_config = {
    "handlers": [
        {
            "sink": "logs/bot.log",
            "format": "{time} | {level} | {message}",
            "encoding": "utf-8",
            "level": "DEBUG",
            "rotation": "2 MB",
            "mode": "a"
        },
    ],
}

USL = ['city',
       'request_date',
       'hotel_count',
       'photo_count',
       'distance',
       'min_price',
       'max_price',
       'date1',
       'date2'
       ]

PHOTO_SIZE = "b"

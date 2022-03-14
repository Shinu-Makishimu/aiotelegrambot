# Bot - an example of working with aiogram
This bot can find hotels in any city in the world


## Requirements

* Python 3.9+
* [aiogram](https://github.com/aiogram/aiogram) – asynchronous framework for Telegram Bot API
* [requests](https://github.com/psf/requests) - Requests is a simple, yet elegant, HTTP library.
* [aioredis](https://aioredis.readthedocs.io/en/latest/) - The library is intended to provide simple and clear interface to Redis based on asyncio.
* [sqlite3](https://www.sqlite.org/) - database engine
* [loguru](https://github.com/Delgan/loguru) 

You need to create an .env file with tokens for telegram and API to run bot.
Variable name for telegram: KEY, for API: APIKEY. Their initialization is done in the settings module

You can install all dependencies by running the following command: `pip install -r requirements.txt`

For correct operation, a running Redis server of version 3.0.504 or higher is required..


## Bot commands

* `/start` - bot launch, performed automatically when connected to the bot.
* `/help` - help message
* `/lowprice` - find cheapest hotels
* `/highprice` - find most expensive hotels
* `/bestdeal` - the best offer for price and distance from the center
* `/history` - menu with requests history, if available


Short instructions for working with the bot. In case of erroneous input, the bot will display a corresponding message and ask you to enter the value again.

### find cheapest hotels

1. Enter the `/lowprice` command. The bot will ask for the city in which you want to search for hotels.
2. Enter the name of the locality. The bot will make a request to the hotels api and return a list of locations whose names are similar to the entered city.
There will also be a button to refuse the proposed results. When you click on it (as well as in the absence of results
search), the bot will ask you to enter the name of the city again.
   
3. bot will ask for the number of hotels you want to display as a result.
4. bot will ask for the number of photos that should be displayed for each hotel.
5. bot will ask you if you want to save the search results. If you agree, the bot will save your history in the database,
on failure, the request parameters will be lost.
6. bot will execute the following request to the hotels api and display a list of hotels with the name, class, price, address,
distance from the center and a link to the location of the hotel on google maps.



### find most expensive hotels

1. 
To get a list of the most expensive hotels, enter the command `/highprice` and follow steps 2 - 7 from the instructions above for the top cheap hotels


### Best deal
1. Enter the `/bestdeal` command. Follow steps 2-5 from the instructions above for the top cheap hotels.
2. The bot will request a search radius from the city center in kilometers. The input must be a positive integer.
Attention! The distance from the city center for the hotel is given by the hotels.com API and is **NOT GUARANTEED**
3. Enter the minimum and maximum price separated by a space. The input must contain only two numbers separated by a space without symbols or letters.
4. The bot will execute the following request to the hotels api and display a list of hotels with the name, class, price, address,
distance from the center and a link to the location of the hotel on google maps.

### Recommends 

1. The name of the city must consist only of letters of the Russian or English alphabet.
2. The price range is two positive integers separated by a space, written on one line.
3. The maximum distance from the city center must be written as a positive integer.
4. The number of displayed hotels is a positive integer. The maximum possible number is 20, the minimum is 1
5. The number of hotel photos is a positive integer. The maximum possible number is 5, the minimum is 0

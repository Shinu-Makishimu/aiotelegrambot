from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from data.API_requests.hotels_finder import get_hotels
from data.API_requests.locations import make_locations_list


class HotelOrder(StatesGroup):
    """
    State store
    """
    waiting_for_city_name_h = State()
    waiting_for_city_answer_h = State()
    waiting_for_hotel_number_h = State()
    waiting_for_photo_number_h = State()
    waiting_for_currency_h = State()
    waiting_for_history_saving_h = State()


async def hotels_start(message: types.Message) -> None:
    """
    This function starts a dialog. After sending the message, the bot waits for input.
    Once entered, the next function is run. The following function will only be called from the specified state
    :param message: message object
    :return:
    """
    message_text = f'You have chosen the search for most cheapest hotels!\n ' \
                   f'Now, send me city name'
    await message.answer(message_text)
    await HotelOrder.waiting_for_city_name_h.set()


async def hotels_buttons(message: types.Message) -> None:
    """
    This function use get_location function from locations.py module,  (API_requests pocket).
    :param message: message object
    :return:
    """
    loc = make_locations_list(message=message)

    if len(loc) < 1 or not loc:
        await message.answer("No result, change query")
        return
    elif loc.get('bad_request'):
        await message.answer('server is not available')
        return
    else:
        city_keyboard = types.InlineKeyboardMarkup()

        for loc_name, loc_id in loc.items():
            city_keyboard.add(types.InlineKeyboardButton(
                text=loc_name,
                callback_data=f'code{loc_id}'
            ))

        city_keyboard.add(types.InlineKeyboardButton(
            text='I want to find another city ',
            callback_data='code_red'
        ))

        await message.answer('Click the button ', reply_markup=city_keyboard)
        await HotelOrder.waiting_for_city_answer_h.set()


async def city_name_chosen(call: types.CallbackQuery, state: FSMContext) -> None:
    if call.data == 'code_red':
        await call.message.answer("Send city name again")
        return

    await state.update_data(city_id=call.data[4:])
    await call.message.answer("How many hotels must be in result ?")
    await HotelOrder.next()
    await HotelOrder.waiting_for_hotel_number_h.set()


async def hotel_count_chosen(message: types.Message, state: FSMContext) -> None:
    if not message.text.isdigit() or 0 > int(message.text) > 20:
        await message.answer("20 hotels- max. Send only numbers. Try again:")
        return

    await state.update_data(hotel_number=message.text)
    await HotelOrder.next()
    await message.answer("How many photos must be for each hotel")
    await HotelOrder.waiting_for_photo_number_h.set()


async def photo_count_chosen(message: types.Message, state: FSMContext) -> None:
    if not message.text.isdigit() or 0 > int(message.text) > 5:
        await message.answer("5 photos- max. Send only numbers. Try again:")
        return

    await state.update_data(photo_number=message.text)
    await HotelOrder.next()
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    text = ('RUB', 'EUR', 'USD')
    keyboard.row(*(types.KeyboardButton(txt) for txt in text))
    await message.answer("Choose your currency:", reply_markup=keyboard)
    await HotelOrder.waiting_for_currency_h.set()


async def currency_chosen(message: types.Message, state: FSMContext) -> None:
    if message.text not in ['RUB', 'EUR', 'USD']:
        await message.answer('Just tap on buttons!')
        return

    await state.update_data(currency=message.text)
    await HotelOrder.next()
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    text = ('YES', 'NO')
    keyboard.row(*(types.KeyboardButton(txt) for txt in text))
    await message.answer("Save query in history?", reply_markup=keyboard)
    await HotelOrder.waiting_for_history_saving_h.set()


async def history_chosen(message: types.Message, state: FSMContext) -> None:
    """
    this function uses the data stored in the FTS to form a dictionary of parameters.
    This dictionary is passed to the function get_hotels (hotels_finer.py module). This function returns the result
    of the request to the API.
    The query results are sent to the chat.
    At the end, the state.finish() method resets state and input data
    :param message:
    :param state:
    :return:
    """
    if message.text not in ['YES', 'NO']:
        await message.answer("Just tap on buttons!")
        return

    await state.update_data(save_history=message.text)
    user_data = await state.get_data()
    language_replace = {
        'ru': 'ru_RU',
        'en': 'en_US'
    }
    language = message.from_user.language_code
    if language != 'ru':
        language = language_replace['en']
    else:
        language = language_replace['ru']
    parameters = {
        'city': user_data['city_id'],
        'hotel_count': user_data['hotel_number'],
        'photo_count': user_data['photo_number'],
        'command': 'lowprice',
        'currency': user_data['currency'],
        'language': language
    }
    await message.answer(
        f"loading, please wait",
        reply_markup=types.ReplyKeyboardRemove()
    )
    hotels = get_hotels(params=parameters)
    if not hotels or len(hotels.keys()) < 1:
        await message.answer('No result. Please, change parameters and try again')
    elif 'bad_request' in hotels:
        await message.answer('Something goes wrong! Try again later')
    else:
        await message.answer(f'Hotels find: {len(hotels.items())}')
        for hotel_id, hotel_info in hotels.items():
            list_of_urls = hotel_info['photo']
            txt = hotel_info['message']
            await message.answer(text=txt, parse_mode='HTML')
            if len(list_of_urls)>0:
                for number, photo in enumerate(list_of_urls):
                    text = f'фото номер {number + 1}'
                    link = f"{photo}"
                    r = f'<a href="{link}">{text}</a>'
                    await message.answer(text=r, parse_mode='HTML')
    await state.finish()


def register_handlers_highprice(dp: Dispatcher) -> None:
    """
    Callback factory
    :param dp: dispatcher object
    :return:
    """
    dp.register_message_handler(hotels_start, commands="highprice", state="*")
    dp.register_message_handler(hotels_buttons, state=HotelOrder.waiting_for_city_name_h)
    dp.register_callback_query_handler(city_name_chosen, state=HotelOrder.waiting_for_city_answer_h)
    dp.register_message_handler(hotel_count_chosen, state=HotelOrder.waiting_for_hotel_number_h)
    dp.register_message_handler(photo_count_chosen, state=HotelOrder.waiting_for_photo_number_h)
    dp.register_message_handler(currency_chosen, state=HotelOrder.waiting_for_currency_h)
    dp.register_message_handler(history_chosen, state=HotelOrder.waiting_for_history_saving_h)

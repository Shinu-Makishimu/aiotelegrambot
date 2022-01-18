

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from data.API_requests.locations import make_locations_list
from data.API_requests.hotels_finder import get_hotels


class HotelOrder(StatesGroup):
    waiting_for_city_name_l = State()
    waiting_for_city_answer_l = State()
    waiting_for_hotel_number_l = State()
    waiting_for_photo_number_l = State()
    waiting_for_currency_l = State()
    waiting_for_history_saving_l = State()


async def hotels_start(message: types.Message):
    message_text = f'Вы выбрали поиск самых нищих отелей\n ' \
                   f'Внимание, в выдаче могут быть хостелы!\n' \
                   f'Теперь вводите название города'
    await message.answer(message_text)
    await HotelOrder.waiting_for_city_name_l.set()


async def hotels_buttons(message: types.Message):

    loc = make_locations_list(message=message)
    if len(loc) < 1 or not loc:
        await message.answer("Ничего не найдено, повторите запрос.")
        return
    elif loc.get('bad_request'):
        await  message.answer('сервер недоступен')
        return
    else:
        city_keyboard = types.InlineKeyboardMarkup()
        for loc_name, loc_id in loc.items():
            city_keyboard.add(types.InlineKeyboardButton(
                text = loc_name,
                callback_data=f'code{loc_id}'
            ))
        city_keyboard.add(types.InlineKeyboardButton(
                text='Нет моего варианта',
                callback_data='codered'
            ))
        await message.answer('Нажмите кнопку', reply_markup=city_keyboard)
        await HotelOrder.waiting_for_city_answer_l.set()


async def city_name_chosen(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'code_red':
        await call.answer("Введите название города повторно")
        return
    await state.update_data(city_id=call.data[4:])
    await call.message.answer("сколько отелей выводить ?")
    await HotelOrder.next()
    await HotelOrder.waiting_for_hotel_number_l.set()


async def hotel_count_chosen(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or 0 > int(message.text) >20:
        await message.answer("20 максимум и ввод должен быть только числами")
        return
    await state.update_data(hotel_number=message.text)

    await HotelOrder.next()
    await message.answer("сколько фотографий показывавть?:",)
    await HotelOrder.waiting_for_photo_number_l.set()


async def photo_count_chosen(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or 0 > int(message.text) > 5:
        await message.answer("5 максимум.")
        return
    await state.update_data(photo_number=message.text)
    await HotelOrder.next()
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    text=('RUB', 'EUR', 'USD')
    keyboard.row(*(types.KeyboardButton(txt) for txt in text))
    await message.answer("Выбери валюту поиска:", reply_markup=keyboard)
    await HotelOrder.waiting_for_currency_l.set()


async def currency_chosen(message: types.Message,state: FSMContext):
    if message.text not in ['RUB', 'EUR', 'USD']:
        await message.answer('Тыкай в кнопки!')
        return

    await state.update_data(currency=message.text)
    await HotelOrder.next()
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    text=('ДА', 'НЕТ')
    keyboard.row(*(types.KeyboardButton(txt) for txt in text))
    await message.answer("сохранить историю?:", reply_markup=keyboard)
    await HotelOrder.waiting_for_history_saving_l.set()


async def history_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in ['да', 'нет']:
        await message.answer("тыкай в кнопки")
        return
    await state.update_data(save_history=message.text)
    user_data = await state.get_data()
    language_replace = {
        'ru':'ru_RU',
        'en':'en_US'
    }
    language = message.from_user.language_code
    if language != 'ru':
        language= language_replace['en']
    else:
        language=language_replace['ru']
    parameters = {
        'city':user_data['city_id'],
        'hotel_count': user_data['hotel_number'],
        'photo_count': user_data['photo_number'],
        'command': 'lowprice',
        'currency': user_data['currency'],
        'language': language
    }
    await message.answer(
        f"Ждем ответа",
        reply_markup=types.ReplyKeyboardRemove()
    )
    hotels = get_hotels(params=parameters)
    if not hotels or len(hotels.keys())<1:
        await message.answer('Ничего не найдено. измените параметры поиска')
    elif 'bad_request' in hotels:
        await message.answer('Что то сломалось на стороне API, попробуйте позже')
    else:
        await message.answer(f'Найдено отелей: {len(hotels.items())}')
        for hotel_id, hotel_info in hotels.items():
            list_of_urls = hotel_info['photo']
            message = hotel_info['message']
            if len(list_of_urls)<1:
                await message.answer(text=message, parse_mode='HTML')
            else:
                media_group = [types.InputMediaPhoto(media=i_elem) for i_elem in list_of_urls]
    await state.finish()


def register_handlers_lowprice(dp: Dispatcher):
    dp.register_message_handler(hotels_start, commands="lowprice", state="*")
    dp.register_message_handler(hotels_buttons, state=HotelOrder.waiting_for_city_name_l)
    dp.register_callback_query_handler(city_name_chosen, state=HotelOrder.waiting_for_city_answer_l)
    dp.register_message_handler(hotel_count_chosen, state=HotelOrder.waiting_for_hotel_number_l)
    dp.register_message_handler(photo_count_chosen, state=HotelOrder.waiting_for_photo_number_l)
    dp.register_message_handler(currency_chosen, state=HotelOrder.waiting_for_currency_l)
    dp.register_message_handler(history_chosen, state=HotelOrder.waiting_for_history_saving_l)

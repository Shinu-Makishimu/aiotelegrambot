
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


from data.API_requests.locations import make_locations_list



class HotelOrder(StatesGroup):
    waiting_for_city_name = State()
    waiting_for_city_answer = State()
    waiting_for_hotel_number = State()
    waiting_for_photo_number = State()
    waiting_for_history_saving = State()


async def hotels_start(message: types.Message, state: FSMContext):
    await state.
    message_text = f'введите название города'
    await message.answer(message_text)
    await HotelOrder.waiting_for_city_name.set()


async def hotels_buttons(message: types.Message, state: FSMContext):
    """
    По идее в месседж должен быть город. тогда в этой функции надо сделать инлайн клавиатуру выбора

    :param message:
    :return:
    """
    loc = make_locations_list(message=message)
    if len(loc) <1 or not loc:
        await message.answer("Ничего не найдено, повторите запрос.")
        return
    elif loc.get('bad_request'):
        await  message.answer('сервер недоступен')
    else:
        #чекнуть возврат
        if len(loc) == 1:
            for loc_name, loc_id in loc.items():
                await  state.update_data(city_name=loc_name, city_id=loc_id)
        else:

            city_keyboard = types.InlineKeyboardMarkup()
            for loc_name, loc_id in loc.items():
                city_keyboard.add(types.InlineKeyboardButton(
                    text = loc_name,
                    callback_data=f'code{loc_id}'
                ))
                await message.answer('жми кнопка', reply_markup=city_keyboard)
        await HotelOrder.waiting_for_city_answer.set()


async def city_name_chosen(call: types.CallbackQuery, state: FSMContext):
    # if message.text.lower() not in available_cites_names:
    #     await message.answer("Пожалуйста, выберите город. используя клавиатуру ниже.")
    #     return

    await state.update_data(city_id=call.data[4:])
    await HotelOrder.next()
    await call.answer("сколько отелей выводить ?:")
    await HotelOrder.waiting_for_hotel_number.set()


# async def hotel_count_chosen(message: types.Message, state: FSMContext):
#     if not message.text.isdigit() or  0 > int(message.text) >20:
#         await message.answer("20 максимум.")
#         return
#     await state.update_data(hotel_number=message.text)
#
#     await HotelOrder.next()
#     await message.answer("сколько фотографий показывавть?:")
#     await HotelOrder.waiting_for_photo_number.set()
#
#
# async def photo_count_chosen(message: types.Message, state: FSMContext):
#     if not message.text.isdigit() or 0 > int(message.text) > 5:
#         await message.answer("5 максимум.")
#         return
#     await state.update_data(photo_number=message.text)
#     await HotelOrder.next()
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     keyboard.add(['да', 'нет'])
#     await message.answer("сохранить историю?:")
#     await HotelOrder.waiting_for_history_saving.set()
#
#
# async def history_chosen(message: types.Message, state: FSMContext):
#     # тут типа происходит сохранение истории или нет
#     if message.text.lower() not in ['да', 'нет']:
#         await message.answer("тыкай в кнопки а не пиши отсебятину даун")
#         return
#     await state.update_data(save_history=message.text)
#
#     user_data = await state.get_data()
#     await message.answer(f"Вы заказали {user_data['city_name']}.\n выводить {user_data['hotel_number']}.\n"
#                          f"фото {user_data['photo_number']} историю сохранять? {message.text}")
#     await state.finish()


def register_handlers_lowprice(dp: Dispatcher):
    dp.register_message_handler(hotels_start, commands="highprice", state="*")
    dp.register_message_handler(hotels_buttons, state=HotelOrder.waiting_for_city_name)
    dp.register_message_handler(city_name_chosen, state=HotelOrder.waiting_for_city_answer)
    # dp.register_message_handler(hotel_count_chosen, state=HotelOrder.waiting_for_hotel_number)
    # dp.register_message_handler(photo_count_chosen, state=HotelOrder.waiting_for_photo_number)
    # dp.register_message_handler(history_chosen, state=HotelOrder.waiting_for_history_saving)

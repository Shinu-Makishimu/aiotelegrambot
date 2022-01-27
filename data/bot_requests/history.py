import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class HotelOrder(StatesGroup):
    """
    State store
    """
    waiting_for_history_answ = State()
    waiting_for_city_answer_l = State()
    waiting_for_hotel_number_l = State()
    waiting_for_photo_number_l = State()
    waiting_for_currency_l = State()
    waiting_for_history_saving_l = State()
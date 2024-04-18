from utils import create_dictionary_from_tuples
from update_db_funcs import get_necessary_order_data
from typing import Tuple, Dict
from telegram.ext import (
    CallbackContext,
)

import dotenv
dotenv.load_dotenv()

necessary_order_keys = (
    "Timestamp", "Prod_case_name", "Prod_case_type",
    "First_Name", "Last_Name", "Contact", "Username",
    "Case_name", "Case_image",
    "Order_device", "Order_device_model",
    "Is_cash_on_delivery", "Full_price", "Payment_image",
    "Delivery_data", "Is_pickup"
)

uk_necessary_order_keys = (
    "Дата і час", "Знайдена модель кейсу", "Тип кейсу",
    "Ім'я клієнта", "Прізвище", "Контактний номер телефону", "Username",
    "Введена користувачем модель кейсу", "Зображення кейсу",
    "Пристрій", "Модель пристрою",
    "Накладний платіж", "Кінцева ціна", "Зображення перед/оплати",
    "Дані доставки", "Самовивіз"
)

exlude_order_keys = ("Case_image", "Payment_image")


def create_order_summary(necessary_keys: Tuple, order_id: int) -> Dict:
    data = create_dictionary_from_tuples(keys=necessary_keys,
                                         values=get_necessary_order_data(order_id),)
    return data


def create_necessary_order_summary(data: Dict, exlude_order_keys: Tuple) -> Dict:
    filtered_data = {key: value for key, value in data.items()
                     if key not in exlude_order_keys}
    return filtered_data


def create_order_translation(filtered_data: Dict,
                             necessary_keys: Tuple,
                             uk_necessary_keys: Tuple) -> Dict:

    translation_dict = create_dictionary_from_tuples(keys=necessary_keys,
                                                     values=uk_necessary_keys,)

    translated_data = {translation_dict.get(key, key):
                       value for key, value in filtered_data.items()}

    return translated_data


def create_order_message_for_manager(necessary_data: Dict) -> str:
    translated_data = create_order_translation(filtered_data=necessary_data,
                                               necessary_keys=necessary_order_keys,
                                               uk_necessary_keys=uk_necessary_order_keys)
    message = "Order details:\n"
    for key, value in translated_data.items():
        if value is not None:
            message += f"{key}: {value}\n"

    return message


async def send_order_message_to_manager_chat(order_id: int,
                                             context: CallbackContext, chat_id: str) -> None:

    order_summary = create_order_summary(order_id=order_id,
                                         necessary_keys=necessary_order_keys)
    necessary_order_summary = create_necessary_order_summary(order_summary,
                                                             exlude_order_keys=exlude_order_keys)
    manager_message = create_order_message_for_manager(necessary_order_summary)
    await context.bot.send_message(chat_id, manager_message)

    images_dict = {"Payment_image": "Зображення перед/оплати",
                   "Case_image": "Зображення кейсу"}

    for key, value in images_dict.items():
        order_img = order_summary[key]
        if order_img:
            await context.bot.send_message(chat_id, value)
            try:
                await context.bot.send_document(chat_id, document=order_img)
            except Exception:
                await context.bot.send_photo(chat_id, photo=order_img)

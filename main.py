from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler,
    CallbackContext,
)


# import db insert functions
from update_db_funcs import (
    db_insert_client,
    db_insert_order,
    db_get_most_recent_order_id,
    db_insert_payment,
    db_insert_payment_image,
    db_insert_delivery,
    db_insert_client_contact,
)

from manager_funcs import (
    send_order_message_to_manager_chat,
)

from search_prod import (
    get_design_by_design,
    get_model_by_design,
    get_case_type_by_design,
    generate_button,
    get_price,
    get_best_list
)

from way_for_pay import get_wfp_link
import random

import json
import emoji
import os
import dotenv
dotenv.load_dotenv()


# states of conversation
(
    CHOOSING_OPTION,
    GET_POP_QUESTION,
    GET_BESTSELLERS,
    GET_SHARES,
    GET_GADGET,
    GET_MODEL,
    GET_MODEL_BY_CALLBACKQUARY,
    GET_CASE_TYPE,
    GET_DESIGN,
    GET_PAYMENT,
    GET_SUBSCRIPTION,
    GET_SEND,
    CHOOSING_SEND,
    NEW_POST,
    TAKE_AWAY,
    ASK_CONTACT,) = range(16)


prepayment_price = 150


def create_next_button() -> InlineKeyboardMarkup:
    '''create next button'''
    return InlineKeyboardMarkup([[InlineKeyboardButton("Next", callback_data="next")]])


async def start(update: Update, context: CallbackContext) -> int:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    if not update.message or not user:
        raise ValueError("user or update doesn't exist")
    # Save client_id to db
    telegram_id = user.id

    if context.user_data is None:
        context.user_data = {}  # Initialize user_data if not present

    context.user_data['prod_data'] = None

    context.user_data['telegram_id'] = telegram_id

    # Insert client row, if not present
    db_insert_client(telegram_id, user)

    # Send messages
    text = ''.join(["Це магазин твоїх улюблених кейсів Orientalcase",
                    f"{emoji.emojize(':white_heart:', language='alias')}\n",
                    "Обери, що цікавить найбільше?"])
    buttons = [
        [InlineKeyboardButton("Зробити замовлення", callback_data="make_order")],
        [InlineKeyboardButton("Відповідь на популярні запитання", callback_data="pop_quest")],
        [InlineKeyboardButton("Хочу побачити бестселери", callback_data="get_bestsellers")],
        [InlineKeyboardButton("Акції та спеціальні пропозиції", callback_data="get_shares")]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.message.reply_html(
        rf"Привіт {user.mention_html()}!")
    await update.message.reply_text(text, reply_markup=keyboard)
    return CHOOSING_OPTION


# function choose option
async def choose_option(update: Update, context: CallbackContext) -> int:
    if not update.callback_query or not update.callback_query.data:
        raise ValueError("update.callback_query or update.callback_query.data doesn't exist")

    query = update.callback_query
    option = update.callback_query.data
    if not query.message or not update.callback_query.message:
        raise ValueError("query.message or  update.callback_query.message doesn't exist")

    if option == "make_order":
        text = "Виберіть, для якого девайсу ви хочете обрати кейс:"

        buttons = [
            [InlineKeyboardButton("iPhone", callback_data="iPhone")],
            [InlineKeyboardButton("AirPods", callback_data="AirPods")],
            [InlineKeyboardButton("MacBook", callback_data="MacBook")],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        await update.callback_query.message.reply_text(text=text, reply_markup=keyboard)
        return GET_GADGET

    elif option == "pop_quest":
        await query.message.edit_text(
            "Ви обрали опцію: Відповідь на популярні запитання",
            reply_markup=create_next_button()
            )
        return GET_POP_QUESTION

    elif option == "get_bestsellers":
        await query.message.reply_text(
            "Ви обрали опцію: Хочу побачити бестселери",
            reply_markup=create_next_button())
        return GET_BESTSELLERS

    elif option == "get_shares":
        await query.message.reply_text(
            "Ви обрали опцію: Акції та спеціальні пропозиції",
            reply_markup=create_next_button())
        return GET_SHARES
    else:
        raise NotImplementedError("your callback data not found")
        # CallbackQueries need to be answered, even if no notification to the user is needed
        # Some clients may have trouble https://core.telegram.org/bots/api#callbackquery


# Popular questions
async def pop_question(update: Update, context: CallbackContext) -> int:
    '''function show all popular question from json'''
    if not update.callback_query or not update.callback_query.message:
        raise ValueError("update.callback_query or update.callback_query.message doesn't exist")
    with open('./data/data.json', encoding='utf-8', mode='r') as file:
        data = json.load(file)
    pop_q = data['pop']
    for elem in pop_q:
        question_text = emoji.emojize(
            '\n\n'.join([f"{key}: {value}" for key, value in elem.items()]), language='alias')
        await update.callback_query.message.reply_text(text=question_text)
    return ConversationHandler.END


# Bestsellers
async def get_bestsellers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.callback_query or not update.callback_query.message:
        raise ValueError("update.callback_query or update.callback_query.message doesn't exist")
    for i in range(len(get_best_list())):
        await update.callback_query.message.reply_text(
            text=str(get_best_list()[i]), parse_mode="HTML")
    return ConversationHandler.END


# Promotions
async def get_shares(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.callback_query or not update.callback_query.message:
        raise ValueError("update.callback_query or update.callback_query.message doesn't exist")
    with open('./data/data.json', encoding='utf-8', mode='r') as file:
        data = json.load(file)
    shares = data['shares']
    for elem in shares:
        await update.callback_query.message.reply_text(text=elem)
    return ConversationHandler.END


# Order flow
# # Get order data
async def get_gadget(update: Update, context: CallbackContext) -> int:
    if not update.callback_query or not update.callback_query.data:
        raise ValueError("update.callback_query or update.callback_query.data doesn't exist")
    gadget = update.callback_query.data
    if not context or not context.user_data:
        raise ValueError("context doesn't exist")

    context.user_data['gadget'] = gadget
    context.user_data['gadget'] = gadget
    if not update.callback_query.message:
        raise ValueError(" update.callback_query.message doesn't exist")
    await update.callback_query.message.reply_text(f"Ви обрали гаджет: {gadget}")
    await update.callback_query.message.reply_text(
        "Надішліть назву або фото кейса, який ви бажаєте замовити")
    return GET_DESIGN


async def get_design(update: Update, context: CallbackContext) -> int:
    if not update.message:
        raise ValueError("update.message doesn't exist")

    if not context or not context.user_data:
        raise ValueError("context doesn't exist")

    if update.message.photo:
        case_image = update.message.photo[-1]
        case_image_id = case_image.file_id
        context.user_data['design'] = None
        context.user_data['case_image'] = case_image_id

        await update.message.reply_text("Ви надіслали фото")
        await update.message.reply_photo(photo=case_image)

    elif update.message.document:
        case_image_doc = update.message.document
        case_image_doc_id = case_image_doc.file_id
        context.user_data['design'] = None
        context.user_data['case_image'] = case_image_doc_id

        await update.message.reply_text("Ви надіслали файл")
        await update.message.reply_document(case_image_doc_id)

    elif update.message.text:

        design = update.message.text

        context.user_data['design'] = design
        context.user_data['case_image'] = None
        prod_data = get_design_by_design(context.user_data['design'], context.user_data['gadget'])
        context.user_data['prod_data'] = prod_data

        await update.message.reply_text(f"Ви обрали пошук дизайну: {design}")

        if prod_data:
            context.user_data['prod_case_name'] = prod_data['title']
            await update.message.reply_text(f"Знайдено наступний кейс: {prod_data['title']}")

            # If there are case types
            if get_case_type_by_design(prod_data=prod_data):
                text = 'Оберіть тип кейсу, який ви бажаєте замовити?'
                buttons = generate_button(get_case_type_by_design(prod_data=prod_data), 1)
                keyboard = InlineKeyboardMarkup(buttons)
                await update.message.reply_text(text=text, reply_markup=keyboard)
                return GET_CASE_TYPE

            # If there are no case types
            elif get_model_by_design(prod_data=prod_data):
                context.user_data['prod_case_type'] = None

                text = 'Oберіть модель пристрою для якого ви обираєте кейс'
                if context.user_data['gadget'] == 'MacBook':
                    buttons = generate_button(get_model_by_design(prod_data=prod_data), 2)
                else:
                    buttons = generate_button(get_model_by_design(prod_data=prod_data), 3)
                keyboard = InlineKeyboardMarkup(buttons)

                await update.message.reply_text(text=text, reply_markup=keyboard)
                return GET_MODEL_BY_CALLBACKQUARY

        else:
            await update.message.reply_text(
                'Нажаль ми не знайшли кейсу з такою назвою, напишіть будь ласка модель пристрою.')
            return GET_MODEL

    await update.message.reply_text('Напишіть будь ласка модель пристрою')
    return GET_MODEL


async def get_case_type(update: Update, context: CallbackContext) -> int:
    if not update.callback_query or not update.callback_query.data:
        raise ValueError("update.callback_query or update.callback_query.data doesn't exist")
    if not context or not context.user_data:
        raise ValueError("context doesn't exist")

    prod_case_type = update.callback_query.data
    context.user_data['prod_case_type'] = prod_case_type

    context.user_data['prod_case_type'] = prod_case_type
    prod_data = get_design_by_design(context.user_data['design'], context.user_data['gadget'])

    text = 'Oберіть модель пристрою для якого ви обираєте кейс'
    if context.user_data['gadget'] == 'MacBook':
        buttons = generate_button(get_model_by_design(prod_data=prod_data), 2)
    else:
        buttons = generate_button(get_model_by_design(prod_data=prod_data), 3)
    keyboard = InlineKeyboardMarkup(buttons)
    if not update.callback_query.message:
        raise ValueError("update.callback_query.message doesn't exist")
    await update.callback_query.message.reply_text(f'Ви обрали кейс: {prod_case_type}')
    await update.callback_query.message.reply_text(text=text, reply_markup=keyboard)
    return GET_MODEL_BY_CALLBACKQUARY


async def get_model(update: Update, context: CallbackContext) -> int:
    if not update.message or not update.message.text:
        raise ValueError("update.message or update.message.text doesn't exist")
    if not context or not context.user_data:
        raise ValueError("context doesn't exist")

    model = update.message.text
    case_image = context.user_data['case_image']
    design = context.user_data['design']
    gadget = context.user_data['gadget']
    telegram_id = context.user_data['telegram_id']
    timestamp = update.message.date
    context.user_data['final_price'] = None

    db_insert_order(telegram_id=telegram_id,
                    gadget=gadget,
                    model=model,
                    timestamp=timestamp,
                    design=design,
                    case_image=case_image)

    order_id = db_get_most_recent_order_id(telegram_id=telegram_id)

    context.user_data['order_id'] = order_id

    text = ''.join([
        "Буде зручно повна оплата чи накладеним платежем з передплатою?",
        f"( передплата {prepayment_price} грн )"])
    button1 = InlineKeyboardButton("Повна оплата ", callback_data="full_price")
    button2 = InlineKeyboardButton("Накладний платіж ", callback_data="after_pay")
    keyboard = InlineKeyboardMarkup([[button1, button2]])

    await update.message.reply_text(f"Ваш пристрій: {model}")
    await update.message.reply_text(text=text, reply_markup=keyboard)
    return GET_PAYMENT


async def get_model_by_callback(update: Update, context: CallbackContext) -> int:
    if not update.callback_query or not update.callback_query.data:
        raise ValueError("update.callback_query or update.callback_query.data doesn't exist")
    if not update.callback_query.message or not update.callback_query.message.date:
        raise ValueError("update.callback_query.message.date doesn't exist")
    if not context or not context.user_data:
        raise ValueError("context doesn't exist")
    model = update.callback_query.data
    context.user_data['model'] = model

    design = context.user_data['design']
    prod_case_name = context.user_data['prod_case_name']
    prod_case_type = context.user_data['prod_case_type']
    gadget = context.user_data['gadget']
    telegram_id = context.user_data['telegram_id']
    timestamp = update.callback_query.message.date
    final_price = get_price(context.user_data['prod_data'], context.user_data)
    context.user_data['final_price'] = final_price

    db_insert_order(
                    telegram_id=telegram_id,
                    gadget=gadget,
                    model=model,
                    timestamp=timestamp,
                    design=design,
                    prod_case_name=prod_case_name,
                    prod_case_type=prod_case_type,
                    is_auto_found=True)

    order_id = db_get_most_recent_order_id(telegram_id=telegram_id)

    context.user_data['order_id'] = order_id
    context.user_data['order_id'] = order_id
    context.user_data['final_price'] = final_price

    # Send message to user
    text = ''.join([
        "Буде зручно повна оплата чи накладеним платежем з передплатою?",
        f"( передплата {prepayment_price} грн )"])
    button1 = InlineKeyboardButton("Повна оплата ", callback_data="full_price")
    button2 = InlineKeyboardButton("Накладний платіж ", callback_data="after_pay")
    keyboard = InlineKeyboardMarkup([[button1, button2]])

    if not update.callback_query.message:
        raise ValueError(" update.callback_query.message doesn't exist")

    await update.callback_query.message.reply_text(f'Ви обрали модель: {model}')
    if final_price > 0:
        await update.callback_query.message.reply_text(f'Ціна товару складає {final_price} грн.')
    await update.callback_query.message.reply_text(text=text, reply_markup=keyboard)
    return GET_PAYMENT


# # Get payment data
async def choose_payment(update: Update, context: CallbackContext) -> int:
    if not update.callback_query or not update.callback_query.data:
        raise ValueError("update.callback_query or update.callback_query.data doesn't exist")
    query = update.callback_query
    option = update.callback_query.data

    if not query.message or not update.callback_query.message:
        raise ValueError("query.message or update.callback_query.message doesn't exist")
    if not context or not context.user_data:
        raise ValueError("context doesn't exist")

    order_id = context.user_data['order_id']
    final_price = context.user_data['final_price']

    if option == "full_price":

        db_insert_payment(
            order_id=order_id,
            is_cash_on_delivery=False,
            final_price=final_price,)
        text = ''.join([
            "Ви обрали повну оплату\n",
            "Відправка протягом 2-х робочих днів після оплати",
            f"{emoji.emojize(':heart:', language='alias')}\n"])
        await query.message.edit_text(text)
        if context.user_data['prod_data']:
            final_price = context.user_data["final_price"]
            productName = f'{context.user_data["design"]} - {context.user_data["model"]}'
            order_id = f'{context.user_data["order_id"]}-{random.randint(10,40)}'

            link_wfp = get_wfp_link(order_id, productName, final_price)
            await query.message.edit_text(
                f"<a href='{link_wfp}'>Посилання на оплату</a>", parse_mode="HTML")
        await update.callback_query.message.reply_text(
            "Реквізити для оплати",
            reply_markup=create_next_button())
        return GET_SEND

    elif option == "after_pay":

        db_insert_payment(
            order_id=order_id,
            is_cash_on_delivery=True,
            final_price=final_price,)

        text = '\n'.join([
            "Ви обрали накладний платіж",
            "Відправка протягом 2-х робочих днів після оплати",
            f"{emoji.emojize(f':white_heart:',language='alias')}",
            "Надішліть будь ласка фото або скріншот чека передоплати",
            "I ми доставимо ваше замовлення Новою поштою"])
        await query.message.reply_text(text=text)
        return GET_SUBSCRIPTION
    else:
        raise NotImplementedError("your callback data not found")
    # await query.answer()


async def get_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update or not update.message:
        raise ValueError(
            "update or update.message or update.message.photo or document doesn't exist")
    if not context or not context.user_data:
        raise ValueError("context doesn't exist")
    order_id = context.user_data['order_id']

    if not update.message.photo and not update.message.document and not update.message.text:
        raise ValueError(
            "User input is not a text, document, or photo")

    if update.message.text:
        await update.message.reply_text("Ви надіслали текст, надішліть будь ласка скріншот")
        return GET_SUBSCRIPTION

    elif update.message.photo:

        payment_image = update.message.photo[-1]
        payment_image_id = payment_image.file_id  # Get the file ID of the photo

        db_insert_payment_image(order_id=order_id,
                                payment_image=payment_image_id)

        await update.message.reply_text("Ви надіслали чек")
        await update.message.reply_photo(
            photo=payment_image_id,
            reply_markup=create_next_button())
        return CHOOSING_SEND

    elif update.message.document:

        payment_image_doc = update.message.document
        payment_image_doc_id = payment_image_doc.file_id

        db_insert_payment_image(order_id=order_id,
                                payment_image=payment_image_doc_id)

        await update.message.reply_text("Ви надіслали файл")
        await update.message.reply_document(document=payment_image_doc_id,
                                            reply_markup=create_next_button())
        return CHOOSING_SEND
    else:
        raise NotImplementedError("your callback data not found")


# # Get delivery data
async def ask_send_delivery(update: Update, context: CallbackContext) -> int:
    if not update.callback_query or not update.callback_query.message:
        raise ValueError("update.callback_query or update.callback_query.data doesn't exist")
    text = "Оберіть варіант доставки"

    button1 = InlineKeyboardButton("Нова пошта", callback_data="new_post")
    button2 = InlineKeyboardButton("Самовивіз", callback_data="take_away")

    keyboard = InlineKeyboardMarkup([[button1, button2]])
    await update.callback_query.message.reply_text(text=text, reply_markup=keyboard)
    return CHOOSING_SEND


async def choose_send_delivery(update: Update, context: CallbackContext) -> int:
    if not update.callback_query or not update.callback_query.data:
        raise ValueError("update.callback_query or update.callback_query.data doesn't exist")
    query = update.callback_query
    option = update.callback_query.data

    if not query.message or not update.callback_query.message:
        raise ValueError("query.message or update.callback_query.message doesn't exist")
    if not context or not context.user_data:
        raise ValueError("context doesn't exist")

    if option in ["new_post", "next"]:
        await query.message.reply_text("Ви обрали Нову Пошту")
        text = '\n'.join([
            "Вкажіть дані для відправки:", "Місто та відділення Нової Пошти",
            "ПІБ", "Номер телефону"])
        await update.callback_query.message.reply_text(text)
        return NEW_POST

    elif option == "take_away":
        order_id = context.user_data['order_id']
        # Insert delivery data
        db_insert_delivery(
            order_id=order_id,
            user_address=None,
            is_pickup=True)

        await query.message.edit_text(
            "Ви обрали самовивіз",
            reply_markup=create_next_button()
            )
        return TAKE_AWAY
    else:
        raise NotImplementedError("your callback data not found")
    # await query.answer()


async def send_address(update: Update, context: CallbackContext) -> int:
    if not update.callback_query or not update.callback_query.message:
        raise ValueError("update.callback_query or update.callback_query.message doesn't exist")
    with open('./data/data.json', encoding='utf-8', mode='r') as file:
        data = json.load(file)
    adress = data['adress']
    message = ''
    for field in adress:
        row = adress[field]
        message += row+'\n'
    await update.callback_query.message.reply_text(text=message)
    text = ''.join([
        " Дякую, ми отримали ваше замовлення,",
        "наш менеджер зв’яжеться з вами якнайшвидше для підтвердження",
        f"{emoji.emojize(':heart:',language='alias')}"])
    await update.callback_query.message.reply_text(text=text)

    await update.callback_query.message.reply_text(
        "Введіть номер телефону, на який менеджер може з вами зв'язатися")
    return ASK_CONTACT


async def get_delivery_info(update: Update, context: CallbackContext) -> int:
    if not update or not update.message:
        raise ValueError("update or update.message doesn't exist")
    if not context or not context.user_data:
        raise ValueError("context doesn't exist")

    user_address = update.message.text
    order_id = context.user_data['order_id']

    # Insert delivery data
    db_insert_delivery(
        order_id=order_id,
        user_address=user_address)

    await update.message.reply_text("Ви написали такі дані")
    await update.message.reply_text(f"{user_address}")
    await update.message.reply_text(
        "Введіть номер телефону, на який менеджер може з вами зв'язатися")
    return ASK_CONTACT


async def ask_contact(update: Update, context: CallbackContext) -> int:
    if not update.message or not update.message.text:
        raise ValueError("update.message or update.message.text doesn't exist")
    if not context or not context.user_data:
        raise ValueError("context doesn't exist")

    contact = update.message.text
    telegram_id = context.user_data['telegram_id']
    order_id = context.user_data['order_id']

    # Update client's contact number
    db_insert_client_contact(telegram_id=telegram_id, contact=contact)

    # Send order summary message to manager user
    manager_chats = {
        "manager_id": os.getenv("MANAGER_ID"),
        "group_id": os.getenv("GROUP_ID"),
             }

    for chat_id in manager_chats.values():
        if chat_id:
            try:
                await send_order_message_to_manager_chat(
                    order_id=order_id,
                    context=context,
                    chat_id=chat_id,
                )
            except Exception as e:
                print(f"Error sending message to chat {chat_id}: {e}")

    await update.message.reply_text(f"Ваш контактний номер: {contact}")
    text = ''.join([" Дякую, ми отримали ваше замовлення,",
                    "наш менеджер зв’яжеться з вами якнайшвидше для підтвердження",
                    f"{emoji.emojize(':heart:',language='alias')}"])
    await update.message.reply_text(text=text)
    return ConversationHandler.END


# Cancel dialog function
async def cancel_dialog(update: Update, context: CallbackContext) -> int:
    if not update or not update.message:
        raise ValueError("update or update.message doesn't exist")
    await update.message.reply_text("Діалог скасовано.")
    return ConversationHandler.END


# Other commands
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        raise ValueError("update.message doesn't exist")
    await update.message.reply_text("Вибач, я не розумію цю команду.")


async def get_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        raise ValueError("update or update.message doesn't exist")
    group_id = update.message.chat_id
    await update.message.reply_text(f"Group ID: {group_id}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    if not update.message:
        raise ValueError("update or update.message doesn't exist")
    await update.message.reply_text("Please write what your search")


def main() -> None:
    """Start the bot.
    Note: It's crucial to ensure that handlers are in correct order
    as they are run one after another.
    """

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(str(os.getenv("TOKEN"))).build()

    '''create ConversationHandler'''
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_OPTION: [CallbackQueryHandler(choose_option)],
            GET_POP_QUESTION: [CallbackQueryHandler(pop_question)],
            GET_SHARES: [CallbackQueryHandler(get_shares)],
            GET_BESTSELLERS: [CallbackQueryHandler(get_bestsellers)],
            GET_GADGET: [CallbackQueryHandler(get_gadget)],
            GET_MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_model)],
            GET_MODEL_BY_CALLBACKQUARY: [CallbackQueryHandler(get_model_by_callback)],
            GET_DESIGN: [MessageHandler(
                filters.TEXT | filters.PHOTO | filters.Document.IMAGE
                & ~filters.COMMAND, get_design)],
            GET_CASE_TYPE: [CallbackQueryHandler(get_case_type)],
            GET_PAYMENT: [CallbackQueryHandler(choose_payment)],
            GET_SEND: [CallbackQueryHandler(ask_send_delivery)],
            GET_SUBSCRIPTION: [MessageHandler(
                filters.TEXT | filters.PHOTO | filters.Document.IMAGE
                & ~filters.COMMAND, get_subscription)],
            CHOOSING_SEND: [CallbackQueryHandler(choose_send_delivery)],
            NEW_POST: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_delivery_info)],
            TAKE_AWAY: [CallbackQueryHandler(send_address)],
            ASK_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_contact)],
        },
        fallbacks=[CommandHandler("start", start), CommandHandler("cancel", cancel_dialog)],

    )

    # Add Conversation Handler
    application.add_handler(conversation_handler)
    # New handler for the get_group_id command
    application.add_handler(CommandHandler("get_group_id", get_group_id))

    # Other handlers
    # on unkown command i.e message -unknown command
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

    # Save message handler
    # application.add_handler(MessageHandler(filters.TEXT, save_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

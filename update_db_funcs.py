from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from db_setup import (
    engine,
)

from db_setup import (
    Client,
    OrderDevice,
    OrderCase,
    Order,
    Payment,
    Delivery,
    )

from telegram import User
from typing import Callable, Any, Tuple
from functools import wraps


# Create a session decorator
def with_session(engine: Engine) -> Callable:
    def decorator(function: Callable) -> Callable:
        @wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            Session = sessionmaker(bind=engine)
            session = Session()

            result = function(session, *args, **kwargs)

            session.close()
            return result
        return wrapper
    return decorator


# Filters
def client_filter_by(session: Session, **kwargs: Any) -> Any:
    telegram_id = kwargs.get('telegram_id')

    if telegram_id:
        return session.query(Client).filter_by(Telegram_id=telegram_id).first()
    else:
        raise Exception("Client not found")


def payment_filter_by(session: Session, **kwargs: Any) -> Any:
    order_id = kwargs.get('order_id')

    if order_id:
        return session.query(Payment).filter_by(Order_id=order_id).first()
    else:
        raise Exception("Order in Payment not found")


# Insert functions
@with_session(engine)
def db_insert_client(session: Session, telegram_id: int, user: User) -> None:
    client = client_filter_by(session, telegram_id=telegram_id)

    if not client:
        # If the client is not present in the table, add the user's information
        new_client = Client(Telegram_id=telegram_id,
                            First_Name=user.first_name,
                            Last_Name=user.last_name,
                            Username=user.username)
        session.add(new_client)
        session.commit()
        print("Console log: new client is added")


@with_session(engine)
def db_insert_order(session: Session, telegram_id: int, timestamp: str, model: str, gadget: str,
                    is_auto_found: bool = False,
                    design: str | None = None, prod_case_name: str | None = None,
                    prod_case_type: str | None = None, case_image: str | None = None) -> None:

    order_device = OrderDevice(Order_device_model=model,
                               Order_device=gadget)
    session.add(order_device)
    session.commit()

    order_case = OrderCase(Case_name=design,
                           Case_image=case_image,
                           Order_device_id=order_device.id,
                           )
    session.add(order_case)
    session.commit()

    client = client_filter_by(session, telegram_id=telegram_id)
    order = Order(
        Client_id=client.id,
        Order_case_id=order_case.id,
        Timestamp=timestamp,
        Prod_case_name=prod_case_name,
        Prod_case_type=prod_case_type,
        Is_auto_found=is_auto_found,
        )

    session.add(order)
    session.commit()

    print("Console log: Order row is created")


@with_session(engine)
def db_get_most_recent_order_id(session: Session, telegram_id: int) -> Any:
    try:
        client = client_filter_by(session, telegram_id=telegram_id)
    except Exception:
        raise Exception("Client not found")

    most_recent_order = (
        session.query(Order)
        .filter_by(Client_id=client.id)
        .order_by(Order.Timestamp.desc())
        .first()
    )

    if most_recent_order is not None:
        return most_recent_order.id
    else:
        raise Exception("No orders found for the client")


@with_session(engine)
def db_insert_payment(session: Session,
                      order_id: int,
                      is_cash_on_delivery: bool,
                      final_price: int) -> None:
    # data from def get_info function

    payment = Payment(
        Is_cash_on_delivery=is_cash_on_delivery,
        Order_id=order_id,
        Full_price=final_price,
                        )

    session.add(payment)
    session.commit()
    print("Console log: Payment row is created")


@with_session(engine)
def db_insert_payment_image(session: Session, order_id: int, payment_image: str) -> None:

    payment = payment_filter_by(session, order_id=order_id)
    payment.Payment_image = payment_image
    payment.Is_payment_provided = True
    session.commit()
    print("Console log: Payment image is updated")


@with_session(engine)
def db_insert_delivery(session: Session,
                       order_id: int,
                       user_address: str,
                       is_pickup: bool = False) -> None:

    delivery = Delivery(
        Delivery_data=user_address,
        Order_id=order_id,
        Is_pickup=is_pickup,)

    session.add(delivery)
    session.commit()

    print("Console log: Delivery row is created")


@with_session(engine)
def db_insert_client_contact(session: Session, telegram_id: int, contact: str) -> None:
    client = client_filter_by(session, telegram_id=telegram_id)

    if client:
        if client.Contact != contact:
            client.Contact = contact
            session.commit()
            print("Console log: Client phone number updated")
    else:
        print("Console log: Client not found")

# Get data functions


@with_session(engine)
def get_necessary_order_data(session: Session, order_id: int) -> Tuple | Any:

    # Join the necessary tables to retrieve the required data
    query = (
        session.query(
            Order.Timestamp, Order.Prod_case_name, Order.Prod_case_type,
            Client.First_Name, Client.Last_Name, Client.Contact, Client.Username,
            OrderCase.Case_name, OrderCase.Case_image,
            OrderDevice.Order_device, OrderDevice.Order_device_model,
            Payment.Is_cash_on_delivery, Payment.Full_price, Payment.Payment_image,
            Delivery.Delivery_data, Delivery.Is_pickup
        )
        .join(Client, Client.id == Order.Client_id)
        .join(OrderCase, OrderCase.id == Order.Order_case_id)
        .join(OrderDevice, OrderDevice.id == OrderCase.Order_device_id)
        .outerjoin(Payment, Payment.Order_id == Order.id)
        .outerjoin(Delivery, Delivery.Order_id == Order.id)
        .filter(Order.id == order_id)
    )

    return query.first()

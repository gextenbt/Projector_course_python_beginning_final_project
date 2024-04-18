from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import ProgrammingError
import os

from typing import Any

'''
Create connection url
'''

current_directory = os.path.dirname(os.path.abspath(__file__))
database_path = os.path.join(current_directory, 'sql_lite_db.db')

DATABASE_URI = f'sqlite:///{database_path}'

engine = create_engine(DATABASE_URI)

'''
Create tables objects
'''
Base: Any = declarative_base()


class Client(Base):
    __tablename__ = 'client'

    id = Column(Integer, primary_key=True, autoincrement=True)
    Telegram_id = Column(BigInteger)
    First_Name = Column(String(50))
    Last_Name = Column(String(50))
    Contact = Column(String(20))
    Username = Column(String(50))


class OrderDevice(Base):
    __tablename__ = 'order_device'

    id = Column(Integer, primary_key=True, autoincrement=True)
    Order_device = Column(String(50))
    Order_device_model = Column(String(50))


class OrderCase(Base):
    __tablename__ = 'order_case'

    id = Column(Integer, primary_key=True, autoincrement=True)
    Order_device_id = Column(Integer, ForeignKey('order_device.id'), nullable=False)

    Case_name = Column(String(50), nullable=True)
    Case_image = Column(String(100), nullable=True)  # link to the telegram id file


class Order(Base):
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True, autoincrement=True)
    Client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
    Order_case_id = Column(Integer, ForeignKey('order_case.id'), nullable=False)
    Timestamp = Column(DateTime)

    Prod_case_name = Column(String(50), nullable=True)
    Prod_case_type = Column(String(50), nullable=True)
    Is_auto_found = Column(Boolean, default=False)


class Payment(Base):
    __tablename__ = 'payment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    Order_id = Column(Integer, ForeignKey('order.id'), nullable=False)
    Full_price = Column(Integer, nullable=True)

    Is_cash_on_delivery = Column(Boolean, default=False)
    Is_pre_paid = Column(Boolean, default=False)
    Payment_image = Column(String(100), nullable=True)  # link to the telegram id file

    Is_full_paid = Column(Boolean, default=False)
    Is_payment_provided = Column(Boolean, default=False)


class Delivery(Base):
    __tablename__ = 'delivery'

    id = Column(Integer, primary_key=True, autoincrement=True)
    Delivery_data = Column(String, nullable=True)
    Order_id = Column(Integer, ForeignKey('order.id'), nullable=False)

    Is_domestic = Column(Boolean, default=True)
    Is_pickup = Column(Boolean, default=False)


if __name__ == "__main__":
    # Create the tables in the database if they don't exist
    try:
        Base.metadata.create_all(engine)
    except ProgrammingError:
        pass

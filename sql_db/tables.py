from sqlalchemy import Column, String, Float, Integer, DateTime
from sql_db.db import Base
import datetime
from sqlalchemy.sql import func


class BitrixApartment(Base):
    __tablename__ = 'bitrix_apartment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    apartment_id = Column(String(255), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    contact = Column(String(255), nullable=True)
    apartment_balance = Column(Float, nullable=True)
    tariff = Column(String(255), nullable=True)
    accrual = Column(String(255), nullable=True)
    privilege = Column(String(255), nullable=True)
    was_accrual_performed = Column(String(255), nullable=True)
    microdistrict = Column(String(255), nullable=False)
    house = Column(String(255), nullable=False)
    apartment = Column(String(255), nullable=False)
    personal_account = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<BitrixApartment(apartment_id={self.apartment_id})>"


class KaspiPayRequest(Base):
    __tablename__ = 'kaspi_pay_request'

    id = Column(Integer, primary_key=True, autoincrement=True)
    txn_id = Column(String(512), unique=True, nullable=False, comment="ID в системе каспи")
    account = Column(String(512), nullable=False, comment="Лицевой счет квартиры")
    date = Column(DateTime, default=datetime.datetime.now, nullable=False, comment="Дата запроса в системе каспи")
    summ = Column(String(512), nullable=False, comment="Сумма пополнения")

    def __repr__(self):
        return f"<KaspiPayRequest(txn_id={self.txn_id}, account={self.account}, date={self.date}, summ={self.summ})>"


class BitrixContact(Base):
    __tablename__ = "bitrix_contact"

    id = Column(Integer, primary_key=True, autoincrement=True)
    contact_id = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<BitrixContact(contact_id={self.contact_id})>"


class UserCheckRequest(Base):
    __tablename__ = "user_check_request"

    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String(512), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(512), nullable=True)

    def __repr__(self):
        return f"<UserCheckRequest(address={self.address}, timestamp={self.timestamp})>"


class PageVisit(Base):
    __tablename__ = "page_visit"

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String(255), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(512), nullable=True)

    def __repr__(self):
        return f"<PageVisit(path={self.path}, timestamp={self.timestamp})>"
    
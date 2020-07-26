import pyodbc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import urllib
import json


Base = declarative_base()
class MonthlyBills(Base):
    __tablename__ = 'monthlyBills'
    id = Column(Integer, primary_key = True)
    bill = Column(String(80), nullable = False)
    cost = Column(Float)
    date = Column(String(2))
    UserID = Column(String(128))
    
class BringHomePay(Base):
    __tablename__ = 'bringHomePay'
    id =Column(Integer, primary_key = True)
    name = Column(String(50), nullable = False)
    amount = Column(Float) 
    dayOfWeek =  Column(String(9))
    Frequency = Column(String(25))
    UserID = Column(String(128), nullable = False)
    
class BankBalance(Base):
    __tablename__ = 'keybalance'
    id =Column(Integer, primary_key = True)
    KeyBalance = Column(Float, nullable = False)
    DateTime = Column(DateTime, nullable = True)
    UserID = Column(String(128), nullable = False)
    AvailableBalance = Column(Float, nullable = True)

class Transactions(Base):
    __tablename__ = 'transactions'
    account_id = Column(String(55), nullable = False)
    account_owner = Column(String(55), nullable = True)
    amount = Column(Float, nullable = False)
    authorized_date = Column(String(55) , nullable = True)
    category = Column(String(55), nullable = True)
    category_id = Column(String(20), nullable = True)
    date = Column(DateTime, nullable = False)
    iso_currency_code = Column(String(55), nullable = True)
    location = Column(String(255), nullable = True)
    merchant_name = Column(String(255), nullable = True)
    name = Column(String(255), nullable = True)
    payment_channel = Column(String(55), nullable = True)
    payment_meta = Column(String(255), nullable = True)
    pending = Column(String(255), nullable = True)
    pending_transaction_id = Column(String(255), nullable = True)
    transaction_code = Column(String(255), nullable = True)
    transaction_id = Column(String(255), primary_key = True)
    transaction_type = Column(String(255), nullable = True)
    unofficial_currency_code = Column(String(255), nullable = True)
import pyodbc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import urllib
import json
import base64
import os
import datetime
import plaid
import json
import time
from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from. import models
class getPlaid():

    def __init__(self):
        # self.credentials_file = os.environ["plaid"]#= 'credentials.json'
        self.PLAID_CLIENT_ID = ''
        self.PLAID_SECRET = ''
        self.PLAID_PUBLIC_KEY = ''
        self.chase_access_token = ''
        self.PLAID_ENV = ''
        self.server = ''
        self.user = ''
        self.password = ''
        self.database = ''
        self.userid = ''        

    def getCredentials(self):
        self.PLAID_ENV = os.getenv('PLAID_ENV', 'development')
        # plaidcreds = os.environ["plaid"]
        # connectionstring = os.environ["connectionstring"]
        # with open(self.credentials_file) as json_file:
        #     data = json.load(json_file)
        self.server = os.environ['server']
        # self.server =   data['codes']['connectionstring']['server']
        self.user = os.environ['user']
        # self.user =     data['codes']['connectionstring']['user']
        self.password = os.environ['password']
        # self.password = data['codes']['connectionstring']['password']
        self.database = os.environ['database']
        # self.database =  data['codes']['connectionstring']['database']
        self.userid = os.environ['userid']
        # self.userid = data['codes']['userid']['id']
        self.PLAID_CLIENT_ID= os.environ['PLAID_CLIENT_ID']
        # self.PLAID_CLIENT_ID =  data['codes']['plaid']['PLAID_CLIENT_ID']
        self.PLAID_SECRET = os.environ['PLAID_SECRET']
        # self.PLAID_SECRET =  data['codes']['plaid']['PLAID_SECRET']
        self.PLAID_PUBLIC_KEY = os.environ['PLAID_PUBLIC_KEY']
        # self.PLAID_PUBLIC_KEY = data['codes']['plaid']['PLAID_PUBLIC_KEY']
        self.chase_access_token = os.environ['chase_access_token']
        # self.chase_access_token =  data['codes']['plaid']['chase_access_token']
        self.client = plaid.Client(client_id = self.PLAID_CLIENT_ID, secret=self.PLAID_SECRET,
                        public_key=self.PLAID_PUBLIC_KEY, environment=self.PLAID_ENV, api_version='2019-05-29')
        self.params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};"
                        "SERVER=" + self.server + ";"
                        "DATABASE=" + self.database + ";"
                        "UID=" + self.user + ";"
                        "PWD=" + self.password)
        return self    
class PlaidBalance():
    
    def __init__(self):
        self.chasebalance = 0

    def getBalance(self):
        PlaidCredentials = getPlaid()
        credentials = PlaidCredentials.getCredentials()
        chase_access_token = credentials.chase_access_token
        try:
            balance_response = credentials.client.Accounts.balance.get(credentials.chase_access_token)
            balances = balance_response['accounts']
            for x in balances:
                if x['name'] == 'TOTAL CHECKING':
                    self.chasebalance = x['balances']['available']
                    print(self.chasebalance)
            return self
        except plaid.errors.PlaidError as e:
            return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })

class PlaidTransactions():

    def getTransactions(self):
        PlaidCredentials = getPlaid()
        credentials = PlaidCredentials.getCredentials()
        chase_access_token = credentials.chase_access_token

        start_date = '{:%Y-%m-%d}'.format(datetime.datetime.now() + datetime.timedelta(-7))
        end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now() + datetime.timedelta(+1))
        print('start date:{} , end date{}'.format(start_date,end_date))
        try:
            transactions_response = credentials.client.Transactions.get(credentials.chase_access_token, start_date, end_date, count = 50)
            return transactions_response
        except plaid.errors.PlaidError as e:
            return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
class updateDatabse():


    PlaidCredentials = getPlaid()
    credentials = PlaidCredentials.getCredentials()
    
    def databaseUpdateBalance(self):
        # gp = getPlaid()
        # plaidCredentials = gp.getCredentials()
        pb = PlaidBalance()
        pbalance = pb.getBalance() 
        # trans = pb.getTransactions()        
        engine = create_engine("mssql+pyodbc:///?odbc_connect={}".format(self.credentials.params))
        DBSession = sessionmaker(bind = engine)    
        session = DBSession()
        bankbalance = session.query(models.BankBalance).filter_by(UserID = self.credentials.userid).one()
        bankbalance.KeyBalance = pbalance.chasebalance
        bankbalance.DateTime = datetime.datetime.now()
        session.add(bankbalance)
        session.commit()

    def databaseUpdateTransactions(self):
        print('start trans')
        pt = PlaidTransactions()
        trans = pt.getTransactions()
  
        transactions = trans['transactions']
        engine = create_engine("mssql+pyodbc:///?odbc_connect={}".format(self.credentials.params))
        DBSession = sessionmaker(bind = engine)   
        for i in transactions:
            # print(i)
            trans = models.Transactions(**i)

            if trans.category != None:
                category_to_string = ' '.join([str(elem) for elem in trans.category])   
                trans.category = category_to_string

            location_to_string = ' '.join([str(elem) for elem in trans.location])   
            trans.location = location_to_string   

            payment_meta_to_string = ' '.join([str(elem) for elem in trans.payment_meta])   
            trans.payment_meta = payment_meta_to_string

            trans.payment_meta = ''
            session = DBSession()
            session.merge(trans)
            session.commit()        
            

def main():
    x = updateDatabse()
    x.databaseUpdateBalance()  
    x.databaseUpdateTransactions()       

main()

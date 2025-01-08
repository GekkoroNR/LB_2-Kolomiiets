from flask import Flask, request
from datetime import datetime, timedelta
import requests
import sqlite3

app = Flask(__name__)

@app.route("/")
def hello_world():
    return 'Hello world'

@app.route('/currency/static', methods = ['GET'])
def get_currency():
    if 'today' in request.args:
        return '1 USD = 41.8 UAH'
    elif 'yesterday' in  request.args:
        return '1 USD = 42.1 UAH'
    else:
        return 'Unknown request'

@app.route('/currency/dinamic', methods = ['GET'])
def get_right_currency():
    if 'today' in request.args:
        date = int(datetime.today().strftime('%Y%m%d'))
    elif 'yesterday' in request.args:
        date = int((datetime.today()-timedelta(1)).strftime('%Y%m%d'))
    else:
        return 'Unknown request'
    response = requests.get(f'https://bank.gov.ua/NBU_Exchange/exchange_site?'
                                  f'start={date}&valcode=usd&json')
    return '1 USD = ' + str(response.json()[0]['rate']) +  ' UAH'

@app.route('/currency/add', methods = ['POST'])
def add_currency_db():
    date = request.json['date'].split('.')
    con = sqlite3.connect('currency_db')
    cursor = con.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Currency (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    price REAL NOT NULL)''')
    response = requests.get(f'https://bank.gov.ua/NBU_Exchange/exchange_site?'
                                  f'start={date[2] + date[1] + date[0]}&valcode=usd&json')
    cursor.execute('INSERT INTO Currency (date, price) VALUES (?, ?)',
                       (request.json['date'], response.json()[0]['rate']))
    con.commit()
    con.close()
    return 'This data was added in currency_db'

@app.route('/currency_format', methods = ['GET'])
def get_format():
    if request.headers['Content-Type'] == 'application/json':
        form = '&json'
    elif request.headers['Content-Type'] == 'application/xml':
        form = '&xml'
    else:
        return 'Unknown format'
    response = requests.get('https://bank.gov.ua/NBU_Exchange/exchange_site?start={0}&valcode='
                            'usd{1}'.format(int(datetime.today().strftime('%Y%m%d')),form))
    if form == '&json':
        return response.json()
    else:
        return response.text

if __name__ == '__main__':
    app.run(port=8000)
from flask import Flask, request
from datetime import datetime, timedelta
import requests

app = Flask(__name__)

@app.route("/")
def hello_world():
    return 'Hello world'

@app.route('/currency/static')
def get_currency():
    if 'today' in request.args:
        return '1 USD = 41.8 UAH'
    elif 'yesterday' in  request.args:
        return '1 USD = 42.1 UAH'
    else:
        return '¯\_(ツ)_/¯'

@app.route('/currency/dinamic')
def get_right_currency():
    if 'today' in request.args:
        date = int(datetime.today().strftime('%Y%m%d'))
    elif 'yesterday' in request.args:
        date = int((datetime.today()-timedelta(1)).strftime('%Y%m%d'))
    else:
        return '¯\_(ツ)_/¯'
    response = requests.get(f'https://bank.gov.ua/NBU_Exchange/exchange_site?'
                                  f'start={date}&valcode=usd&json')
    return '1 USD = ' + str(response.json()[0]['rate']) +  ' UAH'

@app.route('/currency_format')
def get_format():
    if request.headers['Content-Type'] == 'application/json':
        form = '&json'
    elif request.headers['Content-Type'] == 'application/xml':
        form = '&xml'
    else:
        return '¯\_(ツ)_/¯'
    response = requests.get('https://bank.gov.ua/NBU_Exchange/exchange_site?start={0}&valcode='
                            'usd{1}'.format(int(datetime.today().strftime('%Y%m%d')),form))
    if form == '&json':
        return response.json()
    else:
        return response.text

if __name__ == '__main__':
    app.run(port=8000)
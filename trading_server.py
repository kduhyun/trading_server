from flask import Flask, request, jsonify

import yaml
import logging
import os
import TradingOanda
import TradingBybit

##windows: set FLASK_APP=trading_server.py
##linux: export FLASK_APP=trading_server.py
##flask run

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

oandaTokens = os.getenv("OANDA_TOKENS", "").split(",")
tradingOandas = []
for oandaToken in oandaTokens:
    tradingOandas.append(TradingOanda(oandaToken))

bybitApiKeys = os.getenv("BYBIT_API_KEYS", "").split(",")
bybitApiSecrets = os.getenv("BYBIT_API_SECRETS", "").split(",")
tradingBybits = []

for idx in min(len(bybitApiKeys), len(bybitApiSecrets)):
    tradingBybits.append(TradingBybit(bybitApiKeys[idx], bybitApiSecrets[idx]))

def orderInOanda(code, position, price, positionSize, action):
    output = []
    for tradingOanda in tradingOandas:
        output.append(tradingOanda.order(code.upper(), position, price, positionSize, action))    
    return ' '.join(output)

def orderInBybit(code, position, price, positionSize, action):
    output = []
    for tradingBybit in tradingBybits:
        output.append(tradingBybit.order(code.upper(), position, price, positionSize, action))    
    return ' '.join(output)


@app.route('/')
def index():
    return 'Server Works!'

@app.route('/oanda/order/<code>/<position>/<float:price>/with/<float:positionSize>', methods = ['GET','POST'])
def orderForOandaWithPosition(code, position, price, positionSize):

    content = request.json
    action = content['action']

    return orderInOanda(code.upper(), position, price, positionSize, action)

@app.route('/oanda/order/<code>/<float:price>/with/<float:positionSize>', methods = ['GET','POST'])
def orderForOandaWithoutPosition(code, price, positionSize):

    content = request.json
    action = content['action']
    position = content['position']
    
    return orderInOanda(code.upper(), position, price, positionSize, action)


@app.route('/bybit/order/<code>/<position>/<float:price>/with/<float:positionSize>', methods = ['GET','POST'])
def orderForBybitWithPosition(code, position, price, positionSize):
    content = request.json
    action = content['action']

    if price < 0.001:
        price = float(content["price"])

    return orderInBybit(code.upper(), position, price, positionSize, action)

@app.route('/bybit/order/<code>/<float:price>/with/<float:positionSize>', methods = ['GET','POST'])
def orderForBybitWithoutPosition(code, price, positionSize):

    content = request.json
    action = content['action']
    position = content['position']

    if price < 0.001:
        price = float(content["price"])

    return orderInBybit(code.upper(), position, price, positionSize, action)

